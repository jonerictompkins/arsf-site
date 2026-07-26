#!/usr/bin/env python3
"""Build the ARSF prototype with only the Python standard library."""

from __future__ import annotations

import html
import json
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "dist"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def safe(value: object) -> str:
    return html.escape(str(value), quote=True)


def dog_card(dog: dict) -> str:
    traits = "".join(f"<li>{safe(trait)}</li>" for trait in dog["traits"])
    image_path = "." + dog["image"]
    return f"""
            <article class="dog-card">
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


def build() -> None:
    site = load_json(CONTENT / "site.json")
    dogs = [
        load_json(path)
        for path in sorted((CONTENT / "dogs").glob("*.json"))
    ]
    featured = [dog for dog in dogs if dog.get("featured")]
    if not featured:
        raise ValueError("At least one dog must be marked as featured.")

    replacements = {
        key: safe(value)
        for key, value in site.items()
        if not isinstance(value, (dict, list))
    }
    replacements.update(
        {
            "meta_description": safe(site["mission"]),
            "years_serving": str(date.today().year - int(site["founded_year"])),
            "dog_cards": "\n".join(dog_card(dog) for dog in featured),
        }
    )

    template = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        template = template.replace("{{" + key + "}}", value)

    unresolved = [
        fragment.split("}}", 1)[0]
        for fragment in template.split("{{")[1:]
        if "}}" in fragment
    ]
    if unresolved:
        raise ValueError(f"Unresolved template values: {', '.join(unresolved)}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(PUBLIC, OUTPUT)
    (OUTPUT / "index.html").write_text(template, encoding="utf-8")
    print(f"Built {OUTPUT / 'index.html'} with {len(featured)} featured dogs.")


if __name__ == "__main__":
    build()
