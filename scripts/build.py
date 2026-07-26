#!/usr/bin/env python3
"""Build the ARSF static site with only the Python standard library."""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "dist"


def load_json(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def safe(value: object) -> str:
    return html.escape(str(value), quote=True)


def link_attributes(url: str) -> str:
    if url.startswith(("https://", "http://")):
        return ' target="_blank" rel="noopener"'
    return ""


def text_link(label: str, url: str) -> str:
    return (
        f'<a href="{safe(url)}"{link_attributes(url)}>{safe(label)} '
        '<span aria-hidden="true">↗</span></a>'
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "remembered-akita"


def memorial_caption(item: dict) -> str:
    return (
        item["caption"]
        .replace("Click Photo", "")
        .replace("Click to see his video", "Featured in an ARSF video")
        .strip()
    )


def memorial_focus_details(item: dict) -> tuple[str, str]:
    caption = memorial_caption(item)
    date_pattern = re.compile(
        r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}\b"
        r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        r"|\b\d{1,2}/(?:19|20)\d{2}\b"
    )
    dates = list(dict.fromkeys(date_pattern.findall(caption)))
    tagline = date_pattern.sub("", caption)
    tagline = re.sub(r"\s+", " ", tagline).strip(" ,·-–")
    if tagline.lower() in {"", "crossed", "passed"}:
        tagline = "Always remembered"
    return tagline, " · ".join(dates)


def paw_trail() -> str:
    paw = """
      <g>
        <ellipse cx="0" cy="11" rx="13" ry="16"></ellipse>
        <ellipse cx="-16" cy="-5" rx="6" ry="8"></ellipse>
        <ellipse cx="-5" cy="-13" rx="6" ry="8"></ellipse>
        <ellipse cx="8" cy="-13" rx="6" ry="8"></ellipse>
        <ellipse cx="18" cy="-4" rx="6" ry="8"></ellipse>
      </g>"""
    return f"""
      <svg class="paw-trail" viewBox="0 0 330 115" aria-hidden="true">
        <g transform="translate(45 68) rotate(-18)">{paw}</g>
        <g transform="translate(160 42) rotate(14) scale(.8)">{paw}</g>
        <g transform="translate(278 65) rotate(-15) scale(.62)">{paw}</g>
      </svg>"""


def bridge_callout() -> str:
    return f"""
      <section class="bridge-callout">
        <figure>
          <img src="../../images/archive/rainbow-bridge.jpg" alt="Rainbow Bridge artwork preserved from ARSF’s memorial archive" width="526" height="392" loading="lazy">
        </figure>
        <div>
          {paw_trail()}
          <p class="eyebrow">Their steps remain with us</p>
          <h2>Every remembered life has a place here.</h2>
          <p>For the Akitas whose full stories were never written down, ARSF still carries their names forward.</p>
          <a class="text-link" href="../remembering/">Visit the shared remembrance <span aria-hidden="true">→</span></a>
        </div>
      </section>"""


def dog_card(dog: dict, root: str = "./") -> str:
    traits = "".join(f"<li>{safe(trait)}</li>" for trait in dog["traits"])
    image_path = root + dog["image"].lstrip("/")
    return f"""
            <article class="dog-card" data-search="{safe(dog['name'])} {safe(dog['summary'])}">
              <a class="dog-photo" href="{safe(dog['petfinder_url'])}" target="_blank" rel="noopener" aria-label="Meet {safe(dog['name'])} on Petfinder">
                <img src="{safe(image_path)}" alt="{safe(dog['image_alt'])}" width="720" height="760" loading="lazy">
                <span class="dog-status">{safe(dog['status'])}</span>
              </a>
              <div class="dog-body">
                <div class="dog-title">
                  <h3>{safe(dog['name'])}</h3>
                  <span>{safe(dog['age'])} · {safe(dog['sex'])}</span>
                </div>
                <p>{safe(dog['summary'])}</p>
                <ul class="trait-list">{traits}</ul>
                <a class="text-link" href="{safe(dog['petfinder_url'])}" target="_blank" rel="noopener">Meet {safe(dog['name'])} <span aria-hidden="true">↗</span></a>
              </div>
            </article>"""


def resource_card(resource: dict) -> str:
    links = "".join(
        f"<li>{text_link(link['label'], link['url'])}</li>"
        for link in resource["links"]
    )
    return f"""
            <article class="resource-card">
              <span class="resource-number">{safe(resource['number'])}</span>
              <h3>{safe(resource['title'])}</h3>
              <p>{safe(resource['description'])}</p>
              <ul>{links}</ul>
            </article>"""


def card(title: str, description: str, href: str, meta: str = "") -> str:
    meta_markup = f'<span class="card-meta">{safe(meta)}</span>' if meta else ""
    return f"""
        <a class="path-card" href="{safe(href)}"{link_attributes(href)}>
          {meta_markup}
          <h3>{safe(title)}</h3>
          <p>{safe(description)}</p>
          <span class="path-card-link">Explore <span aria-hidden="true">→</span></span>
        </a>"""


def filter_toolbar(label: str, placeholder: str) -> str:
    return f"""
      <div class="collection-toolbar">
        <label for="archive-filter">{safe(label)}</label>
        <input id="archive-filter" type="search" placeholder="{safe(placeholder)}" autocomplete="off" data-archive-filter>
        <p class="filter-status" aria-live="polite" data-filter-status></p>
      </div>"""


def replace_values(template: str, values: dict[str, object]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


def common_values(site: dict, root: str) -> dict[str, str]:
    return {
        **{
            key: safe(value)
            for key, value in site.items()
            if not isinstance(value, (dict, list))
        },
        "root": root,
    }


def partial(name: str, site: dict, root: str) -> str:
    template = (TEMPLATES / "partials" / f"{name}.html").read_text(encoding="utf-8")
    return replace_values(template, common_values(site, root))


def ensure_resolved(markup: str, label: str) -> None:
    unresolved = sorted(
        {
            fragment.split("}}", 1)[0]
            for fragment in markup.split("{{")[1:]
            if "}}" in fragment
        }
    )
    if unresolved:
        raise ValueError(f"{label}: unresolved template values: {', '.join(unresolved)}")


def write_page(
    site: dict,
    slug: str,
    *,
    title: str,
    heading: str | None = None,
    description: str,
    eyebrow: str,
    group: str,
    body: str,
    page_class: str = "",
    output_file: str | None = None,
) -> None:
    output_path = OUTPUT / output_file if output_file else OUTPUT / slug / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    depth = 0 if output_file else len(Path(slug).parts)
    root = "../" * depth
    values = common_values(site, root)
    values.update(
        {
            "page_title": safe(title),
            "page_heading": safe(heading or title),
            "page_description": safe(description),
            "page_eyebrow": safe(eyebrow),
            "page_group": safe(group),
            "page_class": safe(page_class),
            "page_body": body,
            "site_header": partial("header", site, root),
            "site_footer": partial("footer", site, root),
        }
    )
    template = (TEMPLATES / "page.html").read_text(encoding="utf-8")
    markup = replace_values(template, values)
    ensure_resolved(markup, str(output_path.relative_to(ROOT)))
    output_path.write_text(markup, encoding="utf-8")


def article_body(article: dict) -> str:
    notice = ""
    if article.get("review_required"):
        notice = """
          <aside class="review-note">
            <strong>Preserved ARSF resource</strong>
            <p>This material was migrated from ARSF’s public archive. Operational, medical, or program details should be confirmed with ARSF before relying on them.</p>
          </aside>"""
    paragraphs = "\n".join(f"<p>{safe(item)}</p>" for item in article["paragraphs"])
    return f"""
      <section class="page-section">
        <div class="shell reading-layout">
          <article class="prose">
            {notice}
            {paragraphs}
            <div class="source-note">
              <span>Original ARSF archive</span>
              {text_link("View the source page", article["source_url"])}
            </div>
          </article>
        </div>
      </section>"""


def build_article_pages(site: dict, archive: dict) -> None:
    for article in archive["articles"]:
        write_page(
            site,
            article["slug"],
            title=article["title"],
            description=article["summary"],
            eyebrow=article["eyebrow"],
            group=article["group"],
            body=article_body(article),
        )


def build_learn_hub(site: dict, archive: dict) -> None:
    articles = [
        article
        for article in archive["articles"]
        if article["slug"].startswith(("learn/", "health/"))
    ]
    cards = "".join(
        card(
            article["title"],
            article["summary"],
            f"../{article['slug']}/",
            article["eyebrow"],
        )
        for article in articles
    )
    body = f"""
      <section class="page-section">
        <div class="shell">
          <div class="path-grid">{cards}</div>
          <div class="feature-band">
            <div><span>Need practical help?</span><h2>Talk with people who know Akitas.</h2></div>
            <a class="button button-light" href="../contact/">Contact ARSF</a>
          </div>
        </div>
      </section>"""
    write_page(
        site,
        "learn",
        title="Know the Akita",
        description="History, temperament, training, health, and the experience that helps people live responsibly with this powerful, deeply loyal breed.",
        eyebrow="Understanding comes first",
        group="The Akita",
        body=body,
    )


def build_rescue_hub(site: dict, archive: dict, dogs: list[dict]) -> None:
    guides = [
        article
        for article in archive["articles"]
        if article["slug"].startswith("rescue/")
    ]
    guide_cards = "".join(
        card(article["title"], article["summary"], f"../{article['slug']}/", article["eyebrow"])
        for article in guides
    )
    dog_cards = "\n".join(dog_card(dog, "../") for dog in dogs if dog.get("featured"))
    body = f"""
      <section class="page-section page-section-tight">
        <div class="shell action-banner">
          <div><span>Adoption</span><h2>Ready to begin thoughtfully?</h2></div>
          <div class="button-row">
            <a class="button button-coral" href="./apply/">Application and forms</a>
            <a class="button button-quiet" href="{safe(site['petfinder_url'])}" target="_blank" rel="noopener">All available Akitas ↗</a>
          </div>
        </div>
      </section>
      <section class="page-section">
        <div class="shell">
          <div class="section-heading split-heading">
            <div><p class="eyebrow">Currently featured</p><h2>Akitas in ARSF care</h2></div>
            <p>Petfinder remains the source of truth for live availability and full profiles.</p>
          </div>
          <div class="dog-grid">{dog_cards}</div>
        </div>
      </section>
      <section class="page-section page-section-muted">
        <div class="shell">
          <div class="section-heading"><p class="eyebrow">Guidance before displacement</p><h2>Placement resources</h2></div>
          <div class="path-grid">{guide_cards}</div>
          <div class="centered-action"><a class="text-link" href="../resources/rescue-network/">Find another Akita rescue <span aria-hidden="true">→</span></a></div>
        </div>
      </section>"""
    write_page(
        site,
        "rescue",
        title="Rescue and placement",
        description="Intervention, careful evaluation, deliberate matching, and support that continues throughout an Akita’s life.",
        eyebrow="A careful match, never a transaction",
        group="Rescue",
        body=body,
    )


def build_application_page(site: dict, archive: dict) -> None:
    documents = [
        item
        for item in archive["documents"]
        if "application" in item["title"].lower()
    ]
    document_links = "".join(
        f"<li>{text_link(item['title'], item['url'])}</li>" for item in documents
    )
    body = f"""
      <section class="page-section">
        <div class="shell reading-layout">
          <article class="prose">
            <h2>Start with the current online application</h2>
            <p>The application helps ARSF understand your household, experience, environment, and the kind of Akita who may be able to thrive with you. A home check is part of the process.</p>
            <p><a class="button button-coral" href="{safe(site['application_url'])}" target="_blank" rel="noopener">Open ARSF’s Jotform application ↗</a></p>
            <h2>Printable form</h2>
            <ul class="document-list">{document_links}</ul>
            <aside class="review-note">
              <strong>Privacy boundary</strong>
              <p>Applications are handled by ARSF’s existing form service and are never stored in this public website repository.</p>
            </aside>
          </article>
        </div>
      </section>"""
    write_page(
        site,
        "rescue/apply",
        title="Adoption application and forms",
        description="Begin the ARSF adoption conversation online or download a printable application.",
        eyebrow="A deliberate first step",
        group="Rescue and placement",
        body=body,
    )


def build_stories_hub(site: dict, archive: dict) -> None:
    cards = "".join(
        [
            card(
                "Happy Tails",
                "A searchable record of Akitas placed with families.",
                "./happy-tails/",
                f"{len(archive['happy_tails'])} preserved entries",
            ),
            card(
                "Dog Stars",
                "Akitas representing ARSF in television and public appearances.",
                "./dog-stars/",
                f"{len(archive['dog_stars'])} video appearances",
            ),
            card(
                "Feature videos",
                "Films about individual Akitas and the breed community.",
                "./videos/",
                f"{len(archive['feature_videos'])} films",
            ),
            card(
                "ARSF picnics",
                "Four years of community gatherings brought into modern galleries.",
                "./picnics/",
                f"{archive['inventory']['picnic_images']} photographs",
            ),
        ]
    )
    body = f"""
      <section class="page-section">
        <div class="shell">
          <div class="path-grid">{cards}</div>
          <div class="feature-band">
            <div><span>Lives remembered</span><h2>The story continues in the memorial archive.</h2></div>
            <a class="button button-light" href="../memorials/">Visit memorials</a>
          </div>
        </div>
      </section>"""
    write_page(
        site,
        "stories",
        title="Stories and community",
        description="Homecomings, public ambassadors, films, and gatherings that show the breadth of ARSF’s life with Akitas.",
        eyebrow="The lives behind the work",
        group="Archive",
        body=body,
    )


def build_happy_tails(site: dict, archive: dict) -> None:
    cards = []
    for item in archive["happy_tails"]:
        cards.append(
            f"""
          <article class="portrait-card" data-search="{safe(item['name'])} {safe(item['date'])}">
            <img src="{safe(item['image'])}" alt="{safe(item['name'])}, an ARSF Happy Tail" loading="lazy">
            <div><h2>{safe(item['name'])}</h2><p>{safe(item['date'] or 'Adoption archive')}</p></div>
          </article>"""
        )
    body = f"""
      <section class="page-section">
        <div class="shell">
          {filter_toolbar("Find a Happy Tail", "Search by name or date")}
          <div class="portrait-grid" data-filter-grid>{''.join(cards)}</div>
        </div>
      </section>"""
    write_page(
        site,
        "stories/happy-tails",
        title="Happy Tails",
        description=f"{len(cards)} preserved homecomings from ARSF’s public adoption archive.",
        eyebrow="Placed with love",
        group="Stories and community",
        body=body,
    )


def build_dog_stars(site: dict, archive: dict) -> None:
    cards = []
    for item in archive["dog_stars"]:
        poster = (
            f'<img src="{safe(item["poster"])}" alt="{safe(item["name"])} appearing as an ARSF Dog Star" loading="lazy">'
            if item.get("poster")
            else '<div class="media-placeholder">ARSF</div>'
        )
        cards.append(
            f"""
          <article class="media-card" data-search="{safe(item['name'])} {safe(item['date'])}">
            <a href="{safe(item['video'])}" target="_blank" rel="noopener">{poster}<span class="play-mark" aria-hidden="true">▶</span></a>
            <div><h2>{safe(item['name'])}</h2><p>{safe(item['date'])}</p><a href="{safe(item['video'])}" target="_blank" rel="noopener">Watch video ↗</a></div>
          </article>"""
        )
    body = f"""
      <section class="page-section">
        <div class="shell">
          {filter_toolbar("Find a Dog Star", "Search by name or date")}
          <div class="media-grid" data-filter-grid>{''.join(cards)}</div>
        </div>
      </section>"""
    write_page(
        site,
        "stories/dog-stars",
        title="Dog Stars",
        description=f"{len(cards)} television and public appearances preserved from ARSF’s video archive.",
        eyebrow="Akita ambassadors",
        group="Stories and community",
        body=body,
    )


def build_feature_videos(site: dict, archive: dict) -> None:
    cards = []
    for item in archive["feature_videos"]:
        destination = item.get("video") or item["source_url"]
        poster = (
            f'<img src="{safe(item["poster"])}" alt="{safe(item["title"])} video poster" loading="lazy">'
            if item.get("poster")
            else '<div class="media-placeholder">ARSF</div>'
        )
        cards.append(
            f"""
          <article class="media-card" data-search="{safe(item['title'])}">
            <a href="{safe(destination)}" target="_blank" rel="noopener">{poster}<span class="play-mark" aria-hidden="true">▶</span></a>
            <div><h2>{safe(item['title'])}</h2><a href="{safe(destination)}" target="_blank" rel="noopener">Watch film ↗</a></div>
          </article>"""
        )
    body = f"""
      <section class="page-section">
        <div class="shell"><div class="media-grid">{''.join(cards)}</div></div>
      </section>"""
    write_page(
        site,
        "stories/videos",
        title="Feature videos",
        description="Films preserved from ARSF’s public archive—individual stories, tributes, and celebrations of the breed.",
        eyebrow="Watch their stories",
        group="Stories and community",
        body=body,
    )


def build_tribute_pages(site: dict, archive: dict) -> dict[str, str]:
    internal_links = {}
    memorial_by_source = {
        item["tribute_url"]: item
        for item in archive["memorials"]
        if item.get("tribute_url")
    }
    used_slugs: set[str] = set()
    for tribute in archive["tributes"]:
        memorial = memorial_by_source.get(
            tribute["source_url"],
            {
                "name": tribute["name"],
                "caption": tribute["caption"],
                "image": None,
                "orphan": False,
            },
        )
        paragraphs = [
            paragraph
            for paragraph in tribute["paragraphs"]
            if paragraph.strip().lower() != tribute["name"].strip().lower()
        ]
        narrative = "\n".join(f"<p>{safe(item)}</p>" for item in paragraphs)
        if not narrative:
            narrative = (
                "<p>This tribute is preserved primarily through its photographs. "
                "The original ARSF page remains linked below.</p>"
            )
        primary_image = (
            tribute["images"][0]["url"]
            if tribute["images"]
            else memorial.get("image")
        )
        portrait = (
            f'<img src="{safe(primary_image)}" alt="{safe(memorial["name"])}, remembered by the ARSF community" loading="eager">'
            if primary_image
            else (
                '<div class="tribute-photo-missing" role="img" '
                f'aria-label="No photograph is available for {safe(memorial["name"])}">'
                '<span>Remembered<br>with love</span></div>'
            )
        )
        marker = (
            """
              <span class="tribute-orphan-marker">
                <span aria-hidden="true">♥</span>
                <span class="sr-only">ARSF orphan who never found a forever home</span>
              </span>"""
            if memorial.get("orphan")
            else ""
        )
        gallery_images = [
            image
            for image in tribute["images"]
            if image["url"] != primary_image
        ]
        images = "".join(
            f"""
            <a href="{safe(image['url'])}" target="_blank" rel="noopener">
              <img src="{safe(image['url'])}" alt="{safe(image['alt'])}" loading="lazy">
            </a>"""
            for image in gallery_images
        )
        gallery = (
            f'<div class="tribute-gallery">{images}</div>'
            if images
            else ""
        )
        caption = memorial_caption(memorial) or "A life remembered with love."
        body = f"""
      <section class="page-section memorial-tribute">
        <div class="shell">
          <div class="tribute-story-grid">
            <aside class="tribute-portrait{" tribute-portrait--orphan" if memorial.get("orphan") else ""}">
              <figure>{portrait}{marker}</figure>
              <div>
                <span>{"Held forever by ARSF" if memorial.get("orphan") else "Always remembered"}</span>
                <strong>{safe(memorial["name"])}</strong>
                <p>{safe(caption)}</p>
              </div>
            </aside>
            <article class="prose tribute-prose">
              <p class="tribute-lede">A life carried forward in memory.</p>
              {narrative}
              {gallery}
              <div class="source-note">
                <span>Original ARSF tribute</span>
                {text_link("View the preserved source", tribute["source_url"])}
              </div>
            </article>
          </div>
          {bridge_callout()}
        </div>
      </section>"""
        slug = f"memorials/{tribute['slug']}"
        used_slugs.add(tribute["slug"])
        write_page(
            site,
            slug,
            title=tribute["name"],
            description=caption
            or f"A tribute preserved by the ARSF community for {tribute['name']}.",
            eyebrow="Always remembered",
            group="Memorials",
            body=body,
        )
        internal_links[tribute["source_url"]] = f"./{tribute['slug']}/"

    video_by_source = {
        item["source_url"]: item for item in archive["feature_videos"]
    }
    for memorial in archive["memorials"]:
        source_url = memorial.get("tribute_url")
        if not source_url or source_url in internal_links:
            continue
        base_slug = slugify(memorial["name"])
        slug = base_slug
        counter = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(slug)
        video = video_by_source.get(source_url)
        media = ""
        if video and video.get("video"):
            poster = (
                f' poster="{safe(video["poster"])}"'
                if video.get("poster")
                else ""
            )
            media = f"""
              <video class="tribute-video" controls preload="metadata"{poster}>
                <source src="{safe(video["video"])}">
                <a href="{safe(video["video"])}">Watch the preserved ARSF film</a>
              </video>"""
        portrait = (
            f'<img src="{safe(memorial["image"])}" alt="{safe(memorial["name"])}, remembered by the ARSF community" loading="eager">'
            if memorial.get("image")
            else '<div class="tribute-photo-missing"><span>Remembered<br>with love</span></div>'
        )
        caption = memorial_caption(memorial) or "A life remembered with love."
        body = f"""
      <section class="page-section memorial-tribute">
        <div class="shell">
          <div class="tribute-story-grid">
            <aside class="tribute-portrait{" tribute-portrait--orphan" if memorial.get("orphan") else ""}">
              <figure>{portrait}</figure>
              <div>
                <span>{"Held forever by ARSF" if memorial.get("orphan") else "Always remembered"}</span>
                <strong>{safe(memorial["name"])}</strong>
                <p>{safe(caption)}</p>
              </div>
            </aside>
            <article class="prose tribute-prose">
              <p class="tribute-lede">ARSF preserved this remembrance through film.</p>
              <p>Some stories live in voices, movement, and the moments a camera happened to keep. This film remains part of {safe(memorial["name"])}’s place in the ARSF archive.</p>
              {media}
              <div class="source-note">
                <span>Original ARSF film</span>
                {text_link("View the preserved source", source_url)}
              </div>
            </article>
          </div>
          {bridge_callout()}
        </div>
      </section>"""
        write_page(
            site,
            f"memorials/{slug}",
            title=memorial["name"],
            description=caption,
            eyebrow="Always remembered",
            group="Memorials",
            body=body,
        )
        internal_links[source_url] = f"./{slug}/"
    return internal_links


def remembrance_slugs(memorials: list[dict]) -> dict[str, str]:
    slugs: dict[str, str] = {}
    used: set[str] = set()
    for item in memorials:
        if item.get("tribute_url"):
            continue
        base = slugify(item["name"])
        slug = base
        if slug in used:
            _, dates = memorial_focus_details(item)
            date_suffix = slugify(dates)
            slug = f"{base}-{date_suffix}" if dates else f"{base}-2"
        counter = 2
        candidate = slug
        while candidate in used:
            candidate = f"{slug}-{counter}"
            counter += 1
        used.add(candidate)
        slugs[item["source_id"]] = candidate
    return slugs


def remembrance_focus(item: dict) -> str:
    tagline, dates = memorial_focus_details(item)
    portrait = (
        f'<img src="{safe(item["image"])}" '
        f'alt="{safe(item["name"])}, remembered by the ARSF community" '
        'loading="eager">'
        if item.get("image")
        else (
            '<div class="remembrance-focus-placeholder" role="img" '
            f'aria-label="No photograph is available for {safe(item["name"])}">'
            '<span>Remembered<br>with love</span></div>'
        )
    )
    heart = (
        '<span class="remembrance-focus-heart" '
        'aria-label="Held close by ARSF">♥</span>'
        if item.get("orphan")
        else ""
    )
    orphan_attribute = " data-orphan" if item.get("orphan") else ""
    kicker = "Held close by ARSF" if item.get("orphan") else "Remembered by ARSF"
    dates_markup = (
        f'<p class="remembrance-focus-dates">{safe(dates)}</p>'
        if dates
        else ""
    )
    return f"""
          <article class="remembrance-focus" id="remembered-akita"{orphan_attribute}>
            <figure>
              {portrait}
              {heart}
            </figure>
            <div>
              <p class="eyebrow">{kicker}</p>
              <h2>{safe(item["name"])}</h2>
              <p class="remembrance-focus-tagline">{safe(tagline)}</p>
              {dates_markup}
              <p class="remembrance-focus-note">Although no individual tribute was preserved, {safe(item["name"])}’s place in the ARSF community is held here with all the others.</p>
            </div>
          </article>"""


def remembrance_body(
    *,
    orphan_count: int,
    asset_root: str,
    memorials_href: str,
    focus: str = "",
    legacy_links: str = "",
) -> str:
    legacy_data = (
        f'<script type="application/json" id="legacy-remembrance-links">'
        f"{legacy_links}</script>"
        if legacy_links
        else ""
    )
    return f"""
      <section class="page-section remembrance-page" id="shared-remembrance">
        <div class="shell">
          {focus}
          <div class="remembrance-grid">
            <article class="remembrance-copy">
              {paw_trail()}
              <p class="remembrance-explanation">Not every beloved life can be gathered into words.</p>
              <p>Some stories remain in quieter forms: a familiar photograph, a name still spoken with affection, the memory of a watchful presence beside the door or a gentle head resting near someone who needed comfort.</p>
              <p>The Akitas remembered here were each individuals. They had their own expressions, habits, loyalties, and ways of becoming part of a family. Although we may not know every detail of their lives, we know they mattered.</p>
              <div class="remembrance-refrain" aria-label="They were known, loved, and remembered">
                <span>They were known.</span>
                <span>They were loved.</span>
                <span>They are remembered.</span>
              </div>
              <p>Together, these photographs preserve more than a record. They reflect years of companionship, rescue, trust, and devotion shared throughout the ARSF community.</p>
              <h3>Always part of our story</h3>
              <p>The love given to an Akita does not disappear when their life ends. It remains in the people who cared for them, in the homes they changed, and in the work that continues in their memory.</p>
              <a class="button button-light" href="{memorials_href}">Return to all memorials</a>
            </article>
            <div class="remembrance-art">
              <figure>
                <img src="{asset_root}images/archive/rainbow-bridge.jpg" alt="Rainbow Bridge artwork preserved from ARSF’s memorial archive" width="526" height="392">
                <figcaption><em>Rainbow Bridge artwork preserved from the ARSF memorial archive.</em></figcaption>
              </figure>
              <aside>
                <span class="orphan-marker orphan-marker--legend" aria-hidden="true">♥</span>
                <div>
                  <h3>Held close by ARSF</h3>
                  <p>A heart appears beside the names of {orphan_count} Akitas for whom rescue became their final home.</p>
                  <p>They may not have reached a traditional adoptive family, but they were not without one. They were sheltered, cared for, and loved by the ARSF community through the end of their lives.</p>
                  <p>The heart honors that bond.</p>
                </div>
              </aside>
            </div>
          </div>
          {legacy_data}
        </div>
      </section>"""


def build_remembrance_pages(site: dict, archive: dict) -> dict[str, str]:
    orphan_count = sum(bool(item.get("orphan")) for item in archive["memorials"])
    slugs = remembrance_slugs(archive["memorials"])
    legacy_links = json.dumps(
        {
            source_id: f"./{slug}/"
            for source_id, slug in slugs.items()
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    write_page(
        site,
        "memorials/remembering",
        title="Every life leaves something behind",
        description="For the Akitas whose names and photographs remain with us, even when their stories were never written down.",
        eyebrow="Remembered together",
        group="Memorials",
        page_class="remembrance-layout",
        body=remembrance_body(
            orphan_count=orphan_count,
            asset_root="../../",
            memorials_href="../",
            legacy_links=legacy_links,
        ),
    )
    links: dict[str, str] = {}
    for item in archive["memorials"]:
        if item.get("tribute_url"):
            continue
        slug = slugs[item["source_id"]]
        description = (
            f"For {item['name']}, whose place in the ARSF community remains "
            "with us even when a fuller story was never written down."
        )
        write_page(
            site,
            f"memorials/remembering/{slug}",
            title=f"Remembering {item['name']}",
            heading="Every life leaves something behind",
            description=description,
            eyebrow="Remembered together",
            group="Memorials",
            page_class="remembrance-layout",
            body=remembrance_body(
                orphan_count=orphan_count,
                asset_root="../../../",
                memorials_href="../../",
                focus=remembrance_focus(item),
            ),
        )
        links[item["source_id"]] = f"./remembering/{slug}/"
    return links


def build_memorials(
    site: dict,
    archive: dict,
    tribute_links: dict[str, str],
    remembrance_links: dict[str, str],
) -> None:
    cards = []
    for item in archive["memorials"]:
        tribute_url = item.get("tribute_url")
        source = (
            tribute_links[tribute_url]
            if tribute_url
            else remembrance_links[item["source_id"]]
        )
        orphan = bool(item.get("orphan"))
        caption = memorial_caption(item)
        marker = (
            """
                <span class="orphan-marker">
                  <span aria-hidden="true">♥</span>
                  <span class="sr-only">ARSF orphan who never found a forever home</span>
                </span>"""
            if orphan
            else ""
        )
        action = (
            '<span class="memorial-card-link">Read their tribute '
            '<span aria-hidden="true">→</span></span>'
            if tribute_url
            else (
                '<span class="memorial-card-link">Remember them with us '
                '<span aria-hidden="true">→</span></span>'
            )
        )
        portrait = (
            f'<img src="{safe(item["image"])}" alt="{safe(item["name"])}, remembered by the ARSF community" loading="lazy">'
            if item.get("image")
            else (
                '<div class="memorial-photo-missing" role="img" '
                f'aria-label="No photograph is available for {safe(item["name"])}">'
                '<span>Remembered<br>with love</span></div>'
            )
        )
        content = f"""
            <div class="memorial-portrait">
              {portrait}
              {marker}
            </div>
            <div class="memorial-card-copy">
              <span class="memorial-kicker">{"Held forever by ARSF" if orphan else "Always remembered"}</span>
              <strong>{safe(item['name'])}</strong>
              <p>{safe(caption or "A life remembered with love.")}</p>
              {action}
            </div>"""
        content = (
            f'<a href="{safe(source)}" '
            f'aria-label="Remember {safe(item["name"])}">{content}</a>'
        )
        orphan_class = " memorial-card--orphan" if orphan else ""
        cards.append(
            f"""
          <article class="memorial-card{orphan_class}" data-search="{safe(item['name'])} {safe(item['caption'])}">
            {content}
          </article>"""
        )
    orphan_count = sum(bool(item.get("orphan")) for item in archive["memorials"])
    body = f"""
      <section class="page-section memorial-page">
        <div class="shell">
          <div class="memorial-dedication">
            <div>
              <p class="eyebrow">Every life held here mattered</p>
              <h2>They changed the people who knew them.</h2>
              <p>Some found the family they had been waiting for. Some were loved through rescue, foster care, and the final crossing. All of them remain woven into ARSF’s story.</p>
            </div>
            <aside class="orphan-legend">
              <span class="orphan-marker orphan-marker--legend" aria-hidden="true">♥</span>
              <p><strong>Held forever by ARSF</strong>The heart and red border honor {orphan_count} orphans who crossed without ever finding a forever home.</p>
            </aside>
          </div>
          {filter_toolbar("Find a memorial", "Search by name")}
          <div class="memorial-grid" data-filter-grid>{''.join(cards)}</div>
        </div>
      </section>"""
    write_page(
        site,
        "memorials",
        title="Always part of the society",
        description=f"A searchable memorial for {len(cards)} Akitas remembered across ARSF’s public archive.",
        eyebrow="For all our friends who crossed before us",
        group="Memorials",
        body=body,
    )


def build_picnics(site: dict, archive: dict) -> None:
    overview_cards = "".join(
        card(
            f"{group['year']} ARSF picnic",
            "A preserved gallery of the Akitas, families, and volunteers gathered together.",
            f"./{group['year']}/",
            f"{len(group['images'])} photographs",
        )
        for group in archive["picnics"]
    )
    write_page(
        site,
        "stories/picnics",
        title="ARSF picnic archive",
        description=f"{archive['inventory']['picnic_images']} photographs from four years of ARSF community gatherings.",
        eyebrow="Akitas and their people",
        group="Stories and community",
        body=f'<section class="page-section"><div class="shell"><div class="path-grid">{overview_cards}</div></div></section>',
    )

    for group in archive["picnics"]:
        images = "".join(
            f"""
          <a class="gallery-item" href="{safe(url)}" target="_blank" rel="noopener" data-search="{safe(group['year'])} photograph {index}">
            <img src="{safe(url)}" alt="ARSF {safe(group['year'])} picnic photograph {index}" loading="lazy">
          </a>"""
            for index, url in enumerate(group["images"], start=1)
        )
        body = f"""
      <section class="page-section">
        <div class="shell">
          {filter_toolbar("Filter this gallery", "Search photograph number")}
          <div class="photo-grid" data-filter-grid>{images}</div>
        </div>
      </section>"""
        write_page(
            site,
            f"stories/picnics/{group['year']}",
            title=f"The {group['year']} ARSF picnic",
            description=f"{len(group['images'])} photographs preserved from the {group['year']} community gathering.",
            eyebrow="Community gallery",
            group="ARSF picnic archive",
            body=body,
        )


def build_rescue_network(site: dict, archive: dict) -> None:
    cards = []
    for item in archive["rescue_network"]:
        url = item.get("url")
        destination = (
            url
            if url and url.startswith("https://")
            else "https://arsf.org/other_rescues.html"
        )
        cards.append(
            card(
                item["name"],
                item["region"] or "Akita rescue and breed support",
                destination,
                "Rescue network",
            )
        )
    body = f"""
      <section class="page-section">
        <div class="shell">
          <aside class="review-note">
            <strong>Confirm before referral</strong>
            <p>This network is preserved from ARSF’s public links page. Coverage and contact details can change; confirm directly with each organization.</p>
          </aside>
          <div class="path-grid">{''.join(cards)}</div>
        </div>
      </section>"""
    write_page(
        site,
        "resources/rescue-network",
        title="Akita rescue network",
        description="Organizations and breed resources extending Akita support across the United States.",
        eyebrow="Beyond Florida",
        group="Resources",
        body=body,
    )


def build_about(site: dict, archive: dict) -> None:
    story = next(item for item in archive["articles"] if item["slug"] == "about/our-story")
    body = f"""
      <section class="page-section">
        <div class="shell story-grid">
          <div class="story-card story-card-logo">
            <img src="../images/brand/arsf-logo.png" alt="Akita Rescue Society of Florida logo" width="230" height="200">
            <p class="story-year">Since <strong>{safe(site['founded_year'])}</strong></p>
            <p class="story-caption">Serving the Southeast and beyond</p>
          </div>
          <div class="story-copy">
            <p class="eyebrow">Dorie Sparkman and ARSF volunteers</p>
            <h2>A lifetime in service to Akitas</h2>
            <p class="lead">{safe(site['mission'])}</p>
            <p>The society’s work spans education, owner intervention, spay and neuter support, medical advocacy, deliberate adoption, community partnership, and lifelong support.</p>
            <a class="text-link" href="../{safe(story['slug'])}/">Read ARSF’s full history <span aria-hidden="true">→</span></a>
          </div>
        </div>
      </section>
      <section class="page-section page-section-muted">
        <div class="shell path-grid">
          {card("Contact ARSF", "Phone, mailing address, and the best route for questions.", "../contact/", "Start a conversation")}
          {card("Maddie’s Fund archive", "Historical coalition work and annual community statistics.", "../about/maddies-fund/", "Community history")}
          {card("Support the society", "Fund care, foster, transport, or help with supplies.", "../support/", "Carry the work forward")}
        </div>
      </section>"""
    write_page(
        site,
        "about",
        title="A society built around the breed",
        description="The people, programs, judgment, and continuity behind more than four decades of service to Akitas.",
        eyebrow="Stewardship is personal here",
        group="About ARSF",
        body=body,
    )


def build_support(site: dict) -> None:
    body = f"""
      <section class="page-section">
        <div class="shell support-grid">
          <article class="support-panel support-panel-featured">
            <span>01</span><h2>Fund their care</h2>
            <p>Veterinary treatment, food, boarding, transport, and the unplanned needs that arrive with every rescue.</p>
            <a class="button button-light" href="{safe(site['donation_url'])}" target="_blank" rel="noopener">Donate securely ↗</a>
          </article>
          <article class="support-panel">
            <span>02</span><h2>Send what is needed</h2>
            <p>ARSF’s public wish list collects current supply and equipment needs.</p>
            <a class="text-link" href="{safe(site['wishlist_url'])}" target="_blank" rel="noopener">View the wish list ↗</a>
          </article>
          <article class="support-panel">
            <span>03</span><h2>Foster or transport</h2>
            <p>Temporary space and reliable transportation expand what the society can do for an Akita in need.</p>
            <a class="text-link" href="../contact/">Talk with a volunteer →</a>
          </article>
          <article class="support-panel">
            <span>04</span><h2>Shop the legacy collection</h2>
            <p>ARSF’s original merchandise page remains available while its current inventory is confirmed.</p>
            <a class="text-link" href="https://arsf.org/for_sale.html" target="_blank" rel="noopener">See ARSF merchandise ↗</a>
          </article>
        </div>
      </section>"""
    write_page(
        site,
        "support",
        title="Stand with the society",
        description="Financial gifts, supplies, foster homes, transportation, and shared expertise keep Akita rescue moving.",
        eyebrow="Every kind of help matters",
        group="Support ARSF",
        body=body,
    )


def build_contact(site: dict) -> None:
    body = f"""
      <section class="page-section">
        <div class="shell contact-card">
          <div><p class="eyebrow">Call ARSF</p><a class="contact-phone" href="{safe(site['phone_href'])}">{safe(site['phone_display'])}</a><p>Calling is the most reliable route for adoption, fostering, owner support, or an Akita in need.</p></div>
          <div><p class="eyebrow">Mailing address</p><address>{safe(site['mailing_address'])}</address><p><a class="text-link" href="../rescue/apply/">Adoption application and forms →</a></p></div>
        </div>
      </section>"""
    write_page(
        site,
        "contact",
        title="Questions about an Akita?",
        description="Start a conversation with ARSF about adoption, owner support, volunteering, or a dog in need.",
        eyebrow="The breed is personal here",
        group="Contact ARSF",
        body=body,
    )


def build_not_found(site: dict) -> None:
    body = """
      <section class="page-section">
        <div class="shell reading-layout">
          <div class="support-panel">
            <p class="eyebrow">Let’s get you back to the Akitas</p>
            <h2>This page may have moved.</h2>
            <p>Explore breed guidance, rescue and placement help, ARSF stories, and memorials from the main site.</p>
            <a class="button button-primary" href="./">Return home</a>
          </div>
        </div>
      </section>"""
    write_page(
        site,
        "not-found",
        title="Page not found",
        description="The requested ARSF prototype page could not be found.",
        eyebrow="404",
        group="Page not found",
        body=body,
        output_file="404.html",
    )


def build_internal_sitemap(slugs: list[str]) -> None:
    base = "https://arsf.wonderfulrealms.com/"
    urls = [base] + [base + slug.strip("/") + "/" for slug in sorted(slugs)]
    entries = "\n".join(f"  <url><loc>{safe(url)}</loc></url>" for url in urls)
    (OUTPUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n",
        encoding="utf-8",
    )


def build() -> None:
    site = load_json(CONTENT / "site.json")
    resources = load_json(CONTENT / "resources.json")
    archive = load_json(CONTENT / "legacy_archive.json")
    dogs = [load_json(path) for path in sorted((CONTENT / "dogs").glob("*.json"))]
    featured = [dog for dog in dogs if dog.get("featured")]
    if not featured:
        raise ValueError("At least one dog must be marked as featured.")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(PUBLIC, OUTPUT)

    index_values = common_values(site, "./")
    index_values.update(
        {
            "meta_description": safe(site["mission"]),
            "years_serving": str(date.today().year - int(site["founded_year"])),
            "dog_cards": "\n".join(dog_card(dog) for dog in featured),
            "resource_cards": "\n".join(resource_card(resource) for resource in resources),
            "site_header": partial("header", site, "./"),
            "site_footer": partial("footer", site, "./"),
        }
    )
    index_template = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    index_markup = replace_values(index_template, index_values)
    ensure_resolved(index_markup, "dist/index.html")
    (OUTPUT / "index.html").write_text(index_markup, encoding="utf-8")

    build_article_pages(site, archive)
    build_learn_hub(site, archive)
    build_rescue_hub(site, archive, dogs)
    build_application_page(site, archive)
    build_stories_hub(site, archive)
    build_happy_tails(site, archive)
    build_dog_stars(site, archive)
    build_feature_videos(site, archive)
    tribute_links = build_tribute_pages(site, archive)
    remembrance_links = build_remembrance_pages(site, archive)
    build_memorials(site, archive, tribute_links, remembrance_links)
    build_picnics(site, archive)
    build_rescue_network(site, archive)
    build_about(site, archive)
    build_support(site)
    build_contact(site)
    build_not_found(site)

    slugs = [
        str(path.parent.relative_to(OUTPUT))
        for path in OUTPUT.glob("**/index.html")
        if path.parent != OUTPUT
    ]
    build_internal_sitemap(slugs)
    print(
        f"Built {len(slugs) + 1} pages with {len(featured)} featured dogs, "
        f"{len(archive['happy_tails'])} Happy Tails, and "
        f"{len(archive['memorials'])} memorials."
    )


if __name__ == "__main__":
    build()
