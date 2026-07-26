#!/usr/bin/env python3
"""Create a structured manifest of ARSF's public legacy archive.

This is an editorial migration helper, not part of the production build.
It intentionally keeps large photos and videos at their existing public URLs.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "content" / "legacy_archive.json"
SITEMAP_URL = "https://arsf.org/sitemap.xml"
USER_AGENT = "ARSF migration audit (+https://jonerictompkins.github.io/arsf-site/)"

FEATURE_VIDEO_PAGES = {
    "hansel-gretel": ("Hansel and Gretel", "https://arsf.org/hansel_gretel.html"),
    "taz": ("Taz", "https://arsf.org/taz.html"),
    "green-grass-high-tides": (
        "Green Grass and High Tides",
        "https://arsf.org/green_grass_high_tides.html",
    ),
    "akitas-of-florida": (
        "Akitas of Florida: A Celebration",
        "https://arsf.org/akitas_of_florida.html",
    ),
    "yes-to-love": ("Yes to Love", "https://arsf.org/yes_to_love.html"),
    "superheroes": ("Superheroes", "https://arsf.org/superheros.html"),
}

DOCUMENT_TITLES = {
    "arsf_print_and_fill.pdf": "Printable adoption application",
    "quick_ref_bloat.pdf": "Bloat quick-reference card",
    "pet_cpr.pdf": "Pet CPR reference card",
    "heimlich_maneuver.pdf": "Pet Heimlich maneuver reference",
    "ARSF_2010AnnualSummary.pdf": "ARSF 2010 annual statistics",
    "DuvalCounty_2010CommunitySummary.pdf": "Duval County 2010 community statistics",
    "ARSF2012.pdf": "ARSF 2012 statistics",
}

ARTICLE_SPECS = [
    {
        "slug": "about/our-story",
        "group": "About ARSF",
        "eyebrow": "Since 1985",
        "title": "ARSF history and programs",
        "summary": "The society's original account of its founding, education, intervention, spay and neuter, and adoption programs.",
        "url": "https://arsf.org/about_us.html",
        "selector": "#akita_history_text",
        "review_required": True,
    },
    {
        "slug": "learn/akita-history",
        "group": "Know the Akita",
        "eyebrow": "Breed history",
        "title": "A brief history of the Akita",
        "summary": "ARSF's introduction to the Akita's heritage, temperament, loyalty, training needs, and individuality.",
        "url": "https://arsf.org/akita_history.html",
        "selector": "#akita_history_text",
        "review_required": False,
    },
    {
        "slug": "learn/advantages-of-rescue",
        "group": "Know the Akita",
        "eyebrow": "Thoughtful placement",
        "title": "Advantages of adopting an Akita",
        "summary": "Why an evaluated adult rescue can offer valuable knowledge about temperament, health, and fit.",
        "url": "https://arsf.org/advantages.html",
        "selector": "#akita_advantages_text",
        "review_required": True,
    },
    {
        "slug": "learn/akita-coach",
        "group": "Know the Akita",
        "eyebrow": "Each one, teach one",
        "title": "The Akita Coach program",
        "summary": "A referral-based support program designed to connect Akita owners with useful local expertise.",
        "url": "https://arsf.org/akita_coach.html",
        "selector": "#akita_coach_text",
        "review_required": True,
    },
    {
        "slug": "health/bloat-and-emergency",
        "group": "Health and safety",
        "eyebrow": "Know the warning signs",
        "title": "Bloat and emergency resources",
        "summary": "ARSF's collected background on GDV and downloadable emergency reference cards.",
        "url": "https://arsf.org/bloat_information.html",
        "selector": "#bloat_literature_text",
        "review_required": True,
    },
    {
        "slug": "rescue/rehoming",
        "group": "Rescue and placement",
        "eyebrow": "Before a dog loses home",
        "title": "Rehoming information",
        "summary": "ARSF's intervention-first guidance for owners who believe they can no longer keep an Akita.",
        "url": "https://arsf.org/rehome.html",
        "selector": "#rehome_text",
        "review_required": True,
    },
    {
        "slug": "rescue/placement-guide",
        "group": "Rescue and placement",
        "eyebrow": "Responsible placement",
        "title": "Placing your Akita",
        "summary": "Screening, references, home checks, and other considerations from ARSF's original placement guide.",
        "url": "https://arsf.org/placing_your_pet.html",
        "selector": "#placing_tips_text",
        "review_required": True,
    },
    {
        "slug": "rescue/ethics",
        "group": "Rescue and placement",
        "eyebrow": "Standards of care",
        "title": "Akita rescue code of ethics",
        "summary": "The rescue principles and responsibilities preserved from the original ARSF resource.",
        "url": "https://arsf.org/aca_code_of%20_ethics.html",
        "selector": "#code_of_ethics",
        "review_required": True,
    },
    {
        "slug": "about/maddies-fund",
        "group": "About ARSF",
        "eyebrow": "Community partnerships",
        "title": "Maddie's Fund and community statistics",
        "summary": "ARSF's historical Jacksonville coalition material and annual Asilomar reporting archive.",
        "url": "https://arsf.org/maddies_fund.html",
        "selector": "#maddiesfund_text",
        "review_required": True,
    },
]


def fetch(url: str) -> bytes:
    parts = urlsplit(url)
    safe_url = urlunsplit(
        (parts.scheme, parts.netloc, quote(parts.path, safe="/%"), parts.query, "")
    )
    request = Request(safe_url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def soup_for(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch(url), "html.parser")


def clean(value: str) -> str:
    replacements = {
        "\x91": "‘",
        "\x92": "’",
        "\x93": "“",
        "\x94": "”",
        "\x96": "–",
        "\xa0": " ",
    }
    for original, replacement in replacements.items():
        value = value.replace(original, replacement)
    return re.sub(r"\s+", " ", value).strip()


def absolute(page_url: str, value: str | None) -> str | None:
    if not value:
        return None
    return urljoin(page_url, value.replace(" ", "%20"))


def image_name(image) -> str:
    alt = clean(image.get("alt", ""))
    alt = re.sub(r"\s+(photo|picture|image)$", "", alt, flags=re.I)
    if alt and alt.lower() not in {"logo", "woof"}:
        return alt
    stem = Path(urlsplit(image.get("src", "")).path).stem
    return clean(stem.replace("_", " ").replace("-", " ").title())


def happy_tails() -> list[dict]:
    page_url = "https://arsf.org/happy_tails.html"
    soup = soup_for(page_url)
    records = []
    seen = set()
    for image in soup.select('img[src*="happy_tails_photos"]'):
        image_url = absolute(page_url, image.get("src"))
        if not image_url or image_url in seen:
            continue
        seen.add(image_url)
        wrapper = image.find_parent(id=re.compile(r"^adopted\d+$", re.I))
        context = clean(wrapper.get_text(" ", strip=True)) if wrapper else ""
        date_match = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", context)
        records.append(
            {
                "name": image_name(image),
                "date": date_match.group(0) if date_match else "",
                "image": image_url,
                "source_url": page_url,
            }
        )
    return records


def dog_stars() -> list[dict]:
    page_url = "https://arsf.org/dog_stars.html"
    soup = soup_for(page_url)
    records = []
    seen = set()
    for video in soup.find_all("video"):
        source = video.find("source", src=re.compile(r"\.(m4v|mp4)$", re.I))
        video_url = absolute(page_url, source.get("src") if source else None)
        if not video_url or video_url in seen:
            continue
        seen.add(video_url)
        title_block = video.find_previous("div", id=re.compile(r"_title$", re.I))
        title_text = (
            clean(title_block.get_text(" | ", strip=True)) if title_block else ""
        )
        date_match = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", title_text)
        name = title_text.split("|", 1)[0].strip() if title_text else ""
        records.append(
            {
                "name": name or clean(video.get("title", "Dog Star")),
                "date": date_match.group(0) if date_match else "",
                "poster": absolute(page_url, video.get("poster")),
                "video": video_url,
                "source_url": page_url,
            }
        )
    return records


def memorials() -> list[dict]:
    page_url = "https://arsf.org/rainbow.html"
    soup = soup_for(page_url)
    stylesheet = fetch("https://arsf.org/rainbow.css").decode(
        "utf-8",
        errors="replace",
    )
    orphan_stones = {
        stone_id
        for stone_id, rules in re.findall(
            r"#(stone\d+)\s*\{([^}]*)\}",
            stylesheet,
            flags=re.I | re.S,
        )
        if re.search(r"border\s*:\s*2px\s+red\s+solid", rules, flags=re.I)
    }
    records = []
    seen = set()
    for stone in soup.find_all("div", id=re.compile(r"^stone\d+$", re.I)):
        image = stone.find("img")
        image_url = absolute(page_url, image.get("src")) if image else None
        if image_url and image_url in seen:
            continue
        if image_url:
            seen.add(image_url)
        link = image.find_parent("a") if image else stone.find("a", href=True)
        base = soup.find(id=f"{stone.get('id')}_base")
        caption = clean(base.get_text(" ", strip=True)) if base else ""
        strong = stone.find("strong")
        name = (
            clean(next(strong.stripped_strings, ""))
            if strong
            else image_name(image) if image else "Remembered Akita"
        )
        records.append(
            {
                "source_id": stone.get("id"),
                "name": name,
                "caption": caption,
                "image": image_url,
                "orphan": stone.get("id") in orphan_stones,
                "tribute_url": absolute(page_url, link.get("href")) if link else None,
                "source_url": page_url,
            }
        )
    return records


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "remembered-akita"


def tributes(memorial_records: list[dict]) -> list[dict]:
    records = []
    used_slugs: set[str] = set()
    source_records = {
        item["tribute_url"]: item
        for item in memorial_records
        if item.get("tribute_url") and "/memorials/" in item["tribute_url"]
    }
    for source_url, memorial in sorted(source_records.items()):
        soup = soup_for(source_url)
        paragraphs = []
        seen_text = set()
        for element in soup.find_all(["p", "h1", "h2", "h3"]):
            parent_ids = {
                parent.get("id", "")
                for parent in element.parents
                if getattr(parent, "attrs", None)
            }
            if any(
                marker in parent_id.lower()
                for parent_id in parent_ids
                for marker in ("links", "logo", "paypal", "birdies", "back_to_top")
            ):
                continue
            text = clean(element.get_text(" ", strip=True))
            if (
                len(text) < 2
                or text in seen_text
                or text.lower() in {"back to top", "home"}
            ):
                continue
            seen_text.add(text)
            paragraphs.append(text)

        images = []
        seen_images = set()
        for image in soup.find_all("img", src=True):
            source = image.get("src", "")
            alt = clean(image.get("alt", ""))
            if any(
                marker in source.lower()
                for marker in ("arsf_logo", "paypal", "statcounter", "birdies")
            ) or alt.lower() in {"logo", "woof", "web analytics"}:
                continue
            image_url = absolute(source_url, source)
            if image_url and image_url not in seen_images:
                seen_images.add(image_url)
                images.append(
                    {
                        "url": image_url,
                        "alt": alt or f"{memorial['name']} tribute photograph",
                    }
                )

        slug = slugify(memorial["name"])
        counter = 2
        while slug in used_slugs:
            slug = f"{slugify(memorial['name'])}-{counter}"
            counter += 1
        used_slugs.add(slug)
        records.append(
            {
                "slug": slug,
                "name": memorial["name"],
                "caption": memorial["caption"],
                "source_url": source_url,
                "paragraphs": paragraphs,
                "images": images,
            }
        )
    return records


def feature_videos() -> list[dict]:
    records = []
    for slug, (title, page_url) in FEATURE_VIDEO_PAGES.items():
        soup = soup_for(page_url)
        video = soup.find("video")
        source = (
            video.find("source", src=re.compile(r"\.(m4v|mp4)$", re.I))
            if video
            else None
        )
        records.append(
            {
                "slug": slug,
                "title": title,
                "poster": absolute(page_url, video.get("poster")) if video else None,
                "video": absolute(page_url, source.get("src")) if source else None,
                "source_url": page_url,
            }
        )
    return records


def articles() -> list[dict]:
    records = []
    for spec in ARTICLE_SPECS:
        soup = soup_for(spec["url"])
        content = soup.select_one(spec["selector"])
        paragraphs = []
        if content:
            for part in content.get_text("\n", strip=True).splitlines():
                paragraph = clean(part)
                if paragraph and paragraph.lower() != "back to top":
                    paragraphs.append(paragraph)
        records.append(
            {
                key: value
                for key, value in spec.items()
                if key not in {"url", "selector"}
            }
            | {
                "source_url": spec["url"],
                "paragraphs": paragraphs,
            }
        )
    return records


def rescue_network() -> list[dict]:
    page_url = "https://arsf.org/other_rescues.html"
    soup = soup_for(page_url)
    records = []
    ignored_ids = {"links", "home_logo_align", "other_rescues_header"}
    for block in soup.find_all("div", id=True):
        if block.get("id") in ignored_ids or not block.find("h2"):
            continue
        heading = clean(block.find("h2").get_text(" ", strip=True))
        if not heading or heading.lower() == "back to top":
            continue
        link = block.find("a", href=True)
        region = clean(block.find("h3").get_text(" ", strip=True)) if block.find("h3") else ""
        records.append(
            {
                "name": heading,
                "region": region,
                "url": absolute(page_url, link.get("href")) if link else None,
            }
        )
    return records


def main() -> None:
    root = ElementTree.fromstring(fetch(SITEMAP_URL))
    namespace = {"sm": "https://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        clean(node.text or "")
        for node in root.findall("sm:url/sm:loc", namespace)
        if node.text
    ]

    picnic_groups = []
    for year in ("2014", "2015", "2016", "2017"):
        images = [
            url
            for url in urls
            if f"/picnic_{year}_files/" in url
            and re.search(r"\.(jpg|jpeg|png|gif)$", url, re.I)
        ]
        picnic_groups.append(
            {
                "year": year,
                "source_url": f"https://arsf.org/picnic_{year}.html",
                "images": images,
            }
        )

    documents = [
        {
            "title": DOCUMENT_TITLES.get(
                Path(urlsplit(url).path).name,
                clean(Path(urlsplit(url).path).stem.replace("_", " ").title()),
            ),
            "url": url.replace(" ", "%20"),
        }
        for url in urls
        if urlsplit(url).path.lower().endswith(".pdf")
    ]

    html_pages = [
        url.replace(" ", "%20")
        for url in urls
        if re.search(r"\.(html?|HTML?)$", urlsplit(url).path)
    ]

    memorial_records = memorials()
    data = {
        "generated_at": date.today().isoformat(),
        "source_sitemap": SITEMAP_URL,
        "inventory": {
            "sitemap_urls": len(urls),
            "html_pages": len(html_pages),
            "documents": len(documents),
            "picnic_images": sum(len(group["images"]) for group in picnic_groups),
            "orphan_memorials": sum(
                bool(item["orphan"]) for item in memorial_records
            ),
        },
        "happy_tails": happy_tails(),
        "dog_stars": dog_stars(),
        "memorials": memorial_records,
        "tributes": tributes(memorial_records),
        "feature_videos": feature_videos(),
        "articles": articles(),
        "rescue_network": rescue_network(),
        "picnics": picnic_groups,
        "documents": documents,
        "legacy_pages": html_pages,
    }
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        "Imported "
        f"{len(data['happy_tails'])} Happy Tails, "
        f"{len(data['dog_stars'])} Dog Stars, "
        f"{len(data['memorials'])} memorials, and "
        f"{data['inventory']['picnic_images']} picnic images."
    )


if __name__ == "__main__":
    main()
