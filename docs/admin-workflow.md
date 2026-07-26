# Proposed editor workflow

The editing experience should ask Ms. Dorie to manage information, not page layout.

## Routine update

1. Sign into Pages CMS with an approved GitHub account.
2. Open **Featured dogs**.
3. Add or update the dog's name, status, age group, photo, short introduction, traits, and Petfinder link.
4. Turn **Show on homepage** on or off.
5. Save.

The repository retains the change history. A final publishing workflow can either deploy immediately after validation or create a review request first. That choice should be made with ARSF.

## Library and archive update

1. Open **Akita library** to edit the four curated homepage collections.
2. Change the title, short introduction, link labels, or destinations.
3. Upload story and archive photos into the separate archive media library.
4. Save, preview, and publish through the same review workflow.

As Happy Tails and memorials are migrated, they should become their own structured collections with names, dates, stories, images, and tags. Editors should never need to position cards or format a gallery by hand.

## Guardrails

- Navigation, colors, typography, and page structure are not exposed as routine fields.
- Deleting the core site settings file is disabled.
- Dog images are kept in one media library.
- Historical and story imagery is kept in a separate archive library.
- Adoption applications are never stored in Git.
- Every content change can be reviewed and reversed.

## Before inviting editors

- Decide who may edit and who may publish.
- Confirm the final repository visibility and the people who may access Pages CMS.
- Replace prototype copy with ARSF-approved copy.
- Decide whether Petfinder remains the source of truth for all dog details or the new site owns featured summaries.
- Run a short usability session with Ms. Dorie using real update tasks.
