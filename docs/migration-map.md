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

## Migration order

1. Confirm brand, voice, contact details, current links, and the homepage direction.
2. Migrate breed history, advantages, Akita Coach, rehoming, placement, and health resources.
3. Build structured Happy Tails, Dog Stars, and Dorie-curated champion collections.
4. Migrate memorials carefully, preserving original language and attribution.
5. Bring in picnic albums, videos, partner rescues, and remaining downloads.
6. Test routine updates with Dorie before choosing the production editor and publishing rules.
