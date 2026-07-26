# ARSF content migration map

The original site is not a pile of old pages to discard. It is the record of a long-serving breed society. Migration should improve access without flattening the history.

## Collection model

### Akitas

One structured record per dog: name, status, sex, age, location, summary, traits, photos, Petfinder link, intake context, and relationships to later stories or memorials.

Petfinder should remain the source of truth for live availability until ARSF explicitly chooses a different workflow.

### Knowledge and guidance

Long-form articles for breed history, temperament, health, training, owner intervention, rehoming, placement, ethics, and emergency resources. Each record should have a title, summary, body, review date, sources, related downloads, and topic tags.

### Happy Tails and Dog Stars

Stories with a dog name, date, narrative, media, destination or appearance details, and links back to any earlier adoption record. These become browsable and searchable rather than one very long image page.

### Champions and breed ambassadors

A Dorie-curated collection for AKC champions, pedigrees, titles, notable accomplishments, and the dogs who have represented the breed in public. Keep this distinct from Dog Stars, which documents ARSF television and community appearances. Names, titles, dates, and photos need ARSF confirmation before migration.

### Memorials

Individual tributes with a name, dates when known, family or author attribution, story, photos, video, and related dogs. The tone and original wording should be preserved carefully.

### Events and community history

Picnics, classes, public appearances, safety presentations, and other milestones. Each event can own an album instead of requiring a manually laid-out photo page.

### Rescue network and practical resources

Structured links to partner rescues, forms, downloads, assistance programs, and contacts. Each link should have an owner and review date so stale information can be found.

## Database decision

Do not add a hosted database yet. Structured JSON files in Git give this stage:

- a visual editor through Pages CMS;
- durable history and easy rollback;
- no server, credentials, patching, or recurring database cost;
- enough structure to generate category pages and a client-side search index.

The next technical step for a large archive is generated static search, not a database. Move to a managed relational database only if ARSF needs several simultaneous editors, private case workflow, complex cross-record reporting, or direct public submissions.

Adoption applications contain sensitive personal data. They should remain in ARSF's Jotform account and must not be copied into Git or a new database without a separate privacy, retention, access-control, and backup plan.

## Migration status

The first preservation pass is implemented:

1. Breed history, advantages of rescue, Akita Coach, rehoming, placement, ethics, health, ARSF history, and Maddie's Fund resources are internal pages.
2. Happy Tails and Dog Stars are structured, searchable collections.
3. The memorial index and 26 detailed tributes are presented in the new framework.
4. Picnic albums, feature videos, rescue-network entries, and PDF links are discoverable from the new navigation.
5. Historical media remains linked to ARSF's public HTTPS assets to keep the review repository small and preserve source provenance.

Next is editorial migration, not bulk scraping: confirm current guidance, normalize the first frequently edited collection into Pages CMS, assemble Dorie's champion and breed-ambassador collection, and test routine updates with her before choosing final production publishing rules.
