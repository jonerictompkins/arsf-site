#!/usr/bin/env python3
"""Validate editable ARSF content and generated output."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.local_references: list[str] = []
        self.title_depth = 0
        self.title_text: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                error(f"dist/index.html: duplicate id '{element_id}'")
            self.ids.add(element_id)

        if tag == "img" and not values.get("alt"):
            error("dist/index.html: every image needs meaningful alt text")

        if tag == "title":
            self.title_depth += 1

        for attribute in ("href", "src"):
            reference = values.get(attribute)
            if (
                reference
                and not reference.startswith(("#", "https://", "http://", "mailto:", "tel:", "data:"))
            ):
                self.local_references.append(reference)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def error(message: str) -> None:
    ERRORS.append(message)


def load(path: Path) -> dict | list:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: {exc}")
        return {}


def require(data: dict, fields: tuple[str, ...], label: str) -> None:
    for field in fields:
        if field not in data or data[field] in ("", None, []):
            error(f"{label}: missing required field '{field}'")


def require_https(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        error(f"{label}: expected a complete https URL")


site_path = ROOT / "content" / "site.json"
site_data = load(site_path)
if isinstance(site_data, dict):
    site = site_data
else:
    error("content/site.json: expected an object")
    site = {}
require(
    site,
    (
        "organization",
        "hero_title",
        "hero_text",
        "mission",
        "phone_display",
        "phone_href",
        "petfinder_url",
        "application_url",
        "donation_url",
    ),
    "content/site.json",
)
for field in ("petfinder_url", "application_url", "donation_url", "wishlist_url"):
    if site.get(field):
        require_https(site[field], f"content/site.json:{field}")

resources_path = ROOT / "content" / "resources.json"
resources = load(resources_path)
if not isinstance(resources, list) or not resources:
    error("content/resources.json: add at least one resource collection")
else:
    for index, resource in enumerate(resources, start=1):
        label = f"content/resources.json:item {index}"
        if not isinstance(resource, dict):
            error(f"{label}: expected an object")
            continue
        require(resource, ("number", "title", "description", "links"), label)
        links = resource.get("links")
        if not isinstance(links, list) or not links:
            error(f"{label}: add at least one link")
            continue
        for link_index, link in enumerate(links, start=1):
            link_label = f"{label}:link {link_index}"
            if not isinstance(link, dict):
                error(f"{link_label}: expected an object")
                continue
            require(link, ("label", "url"), link_label)
            if link.get("url"):
                if not (
                    link["url"].startswith("./")
                    or urlparse(link["url"]).scheme == "https"
                ):
                    error(f"{link_label}:url: expected a local path or complete https URL")

dog_paths = sorted((ROOT / "content" / "dogs").glob("*.json"))
if not dog_paths:
    error("content/dogs: add at least one dog")

for path in dog_paths:
    label = str(path.relative_to(ROOT))
    dog_data = load(path)
    if not isinstance(dog_data, dict):
        error(f"{label}: expected an object")
        continue
    dog = dog_data
    require(
        dog,
        (
            "name",
            "featured",
            "status",
            "age",
            "sex",
            "location",
            "image",
            "image_alt",
            "summary",
            "traits",
            "petfinder_url",
        ),
        label,
    )
    if dog.get("petfinder_url"):
        require_https(dog["petfinder_url"], f"{label}:petfinder_url")
    if dog.get("image"):
        local_image = ROOT / "public" / dog["image"].lstrip("/")
        if not local_image.is_file():
            error(f"{label}: image not found at {local_image.relative_to(ROOT)}")
    if dog.get("traits") and not isinstance(dog["traits"], list):
        error(f"{label}: traits must be a list")

archive_path = ROOT / "content" / "legacy_archive.json"
archive_data = load(archive_path)
if isinstance(archive_data, dict):
    archive = archive_data
else:
    error("content/legacy_archive.json: expected an object")
    archive = {}

for field in (
    "inventory",
    "happy_tails",
    "dog_stars",
    "memorials",
    "tributes",
    "feature_videos",
    "articles",
    "rescue_network",
    "picnics",
    "documents",
):
    if field not in archive or not archive[field]:
        error(f"content/legacy_archive.json: missing archive collection '{field}'")

article_slugs: set[str] = set()
for index, article in enumerate(archive.get("articles", []), start=1):
    label = f"content/legacy_archive.json:article {index}"
    if not isinstance(article, dict):
        error(f"{label}: expected an object")
        continue
    require(
        article,
        ("slug", "group", "eyebrow", "title", "summary", "source_url", "paragraphs"),
        label,
    )
    slug = article.get("slug")
    if slug in article_slugs:
        error(f"{label}: duplicate slug '{slug}'")
    if slug:
        article_slugs.add(slug)
    if article.get("source_url"):
        require_https(article["source_url"], f"{label}:source_url")

output_root = ROOT / "dist"
html_paths = sorted(output_root.glob("**/*.html"))
if not html_paths:
    error("dist: run scripts/build.py first")
else:
    for output in html_paths:
        label = str(output.relative_to(ROOT))
        markup = output.read_text(encoding="utf-8")
        for fragment in ("{{", "href=\"http://", "src=\"http://"):
            if fragment in markup:
                error(f"{label}: unexpected fragment {fragment!r}")
        parser = SiteParser()
        parser.feed(markup)
        if not "".join(parser.title_text).strip():
            error(f"{label}: page title is missing")
        for reference in parser.local_references:
            clean_reference = reference.split("?", 1)[0].split("#", 1)[0]
            if not clean_reference:
                continue
            resolved = (output.parent / clean_reference).resolve()
            try:
                resolved.relative_to(output_root.resolve())
            except ValueError:
                error(f"{label}: local reference escapes dist: {reference}")
                continue
            if not resolved.exists():
                error(f"{label}: local reference not found: {reference}")

stylesheet = ROOT / "dist" / "styles" / "site.css"
if stylesheet.is_file():
    css = stylesheet.read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        error("dist/styles/site.css: unbalanced braces")

if ERRORS:
    print("Validation failed:", file=sys.stderr)
    for item in ERRORS:
        print(f"- {item}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"Validated site content, {len(resources) if isinstance(resources, list) else 0} "
    f"resource collections, {len(dog_paths)} dogs, {len(html_paths)} pages, "
    "and generated archive output."
)
