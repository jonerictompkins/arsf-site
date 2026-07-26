# ARSF society website prototype

An independent redesign prototype for the Akita Rescue Society of Florida. It is not connected to ARSF's production website or repository.

The generated site currently contains 56 responsive primary pages spanning Akita education, rescue and placement, Happy Tails, Dog Stars, feature videos, memorials, picnic galleries, practical resources, and society information, plus a dedicated 404 page.

## Why this shape

- The deployed site is plain static HTML, CSS, JavaScript, and images.
- A dependency-free Python script assembles structured, editable content into the site.
- Pages CMS can give approved GitHub collaborators a form-based editor for site basics, the Akita library, dog profiles, and photos.
- There is no database, plugin patching, or application server to maintain.
- GitHub Actions can validate and publish the generated static site to GitHub Pages.
- Relative asset URLs allow the same build to work at `/`, `/arsf/`, or a preview host.

## Editorial direction

ARSF is presented as a society for the betterment, placement, understanding, and remembrance of Akitas—not as a product or transactional adoption catalog. The information architecture gives equal dignity to:

- Akita history, temperament, health, and owner guidance
- intervention, rescue, adoption, and responsible placement
- Happy Tails, public ambassadors, gatherings, and community history
- memorials and individual lives worth preserving
- Dorie Sparkman and the volunteers whose experience sustains the work

## Local preview

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8080 --directory dist
```

Then open `http://localhost:8080`.

## Editing content

- Organization details and major links: `content/site.json`
- Akita library collections: `content/resources.json`
- Featured dog profiles: `content/dogs/*.json`
- Imported public-site archive snapshot: `content/legacy_archive.json`
- Dog photos: `public/images/dogs/`
- Admin editor schema: `.pages.yml`

When the repository is connected to GitHub, an approved editor can sign into [Pages CMS](https://app.pagescms.org), choose the repository, and edit these fields without touching code. Publishing and review rules will be finalized with ARSF before any production handoff.

Do not hand-edit `content/legacy_archive.json`. It is a generated preservation snapshot; see `docs/archive-refresh.md` for the deliberate refresh workflow.

## Review boundaries

- This is a public review environment, not yet ARSF's production replacement.
- Adoption submissions go directly to ARSF's current Jotform and are never stored in this repository.
- Donations still go to ARSF's existing Square site.
- Dog profiles are a curated preview based on current public Petfinder listings; ARSF must confirm them before launch.
- Imported operational, medical, contact, and program details need ARSF review before an official launch.
- Archive media remains linked to ARSF's public HTTPS assets; the structured text snapshot and generated pages live here.

See `docs/content-audit.md`, `docs/migration-map.md`, `docs/archive-refresh.md`, `docs/deployment.md`, and `docs/admin-workflow.md` for the content and handoff plan.
