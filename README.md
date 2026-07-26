# ARSF website prototype

An independent, private-first redesign prototype for the Akita Rescue Society of Florida. It is not connected to ARSF's production website or repository.

## Why this shape

- The deployed site is plain static HTML, CSS, JavaScript, and images.
- A dependency-free Python script assembles editable content into the site.
- Pages CMS can give approved GitHub collaborators a form-based editor for site basics, dog profiles, and photos.
- There is no database, plugin patching, or application server to maintain.
- Relative asset URLs allow the same build to work at `/`, `/arsf/`, or a preview host.

## Local preview

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8080 --directory dist
```

Then open `http://localhost:8080`.

## Editing content

- Organization details and major links: `content/site.json`
- Featured dog profiles: `content/dogs/*.json`
- Dog photos: `public/images/dogs/`
- Admin editor schema: `.pages.yml`

When the repository is connected to GitHub, an approved editor can sign into [Pages CMS](https://app.pagescms.org), choose the repository, and edit these fields without touching code. Publishing and review rules will be finalized with ARSF before any production handoff.

## Current boundaries

- This is a homepage and primary-journey prototype, not a production replacement.
- Adoption submissions still go to ARSF's existing application.
- Donations still go to ARSF's existing Square site.
- Dog profiles are a curated preview based on current public Petfinder listings; ARSF must confirm them before launch.
- Deployment is intentionally not automated yet.

See `docs/content-audit.md`, `docs/deployment.md`, and `docs/admin-workflow.md` for decisions still to make.
