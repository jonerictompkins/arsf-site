# Proposed editor workflow

The editing experience should ask Ms. Dorie to manage information, not page layout.

## Routine update

1. Sign into Pages CMS with an approved GitHub account.
2. Open **Featured dogs**.
3. Add or update the dog's name, status, age group, photo, short introduction, traits, and Petfinder link.
4. Turn **Show on homepage** on or off.
5. Save.

The repository retains the change history. A final publishing workflow can either deploy immediately after validation or create a review request first. That choice should be made with ARSF.

## Guardrails

- Navigation, colors, typography, and page structure are not exposed as routine fields.
- Deleting the core site settings file is disabled.
- Dog images are kept in one media library.
- Adoption applications are never stored in Git.
- Every content change can be reviewed and reversed.

## Before inviting editors

- Decide who may edit and who may publish.
- Confirm whether the repository remains private.
- Replace prototype copy with ARSF-approved copy.
- Decide whether Petfinder remains the source of truth for all dog details or the new site owns featured summaries.
- Run a short usability session with Ms. Dorie using real update tasks.
