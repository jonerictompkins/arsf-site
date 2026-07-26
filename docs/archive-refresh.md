# Archive refresh

`content/legacy_archive.json` is a generated preservation snapshot of ARSF's public sitemap and source pages. It is committed so normal builds remain deterministic, offline, and dependency-free.

Do not refresh it during routine site builds and do not hand-edit it. A refresh can change hundreds of records and should always receive an editorial diff review.

## Deliberate refresh

Create an isolated local environment and install the importer's only optional dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install beautifulsoup4
```

Then import, rebuild, and validate:

```bash
.venv/bin/python scripts/import_legacy.py
python3 scripts/build.py
python3 scripts/check.py
git diff -- content/legacy_archive.json
```

The importer:

- downloads ARSF's public sitemap and selected public pages;
- normalizes legacy punctuation and relative media URLs;
- preserves the source stone ID and red-border orphan designation from ARSF's memorial stylesheet;
- extracts archive records and full article text;
- leaves media at its public ARSF HTTPS location;
- does not submit forms, access private data, or alter the source site.

## Review checklist

- Compare collection counts with the previous snapshot.
- Look for renamed, removed, or duplicated dogs.
- Read any changed operational, health, contact, placement, or program guidance.
- Confirm that source and media URLs use HTTPS.
- Rebuild and run the complete validator before committing.
- Keep adoption application responses and other sensitive case information out of Git.
