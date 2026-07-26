# Deployment options

## Current host finding

`wonderfulrealms.com` is served by GoDaddy Websites + Marketing. That product accepts custom-code sections, but it is not a general file host where this project can simply be uploaded into an `/arsf` directory.

## Recommended demo route

Use GitHub Pages at `arsf.wonderfulrealms.com`, matching the existing Wonderful Realms site-project pattern. This is isolated from the GoDaddy-managed main site, requires only a subdomain DNS record, and can later be removed without changing the main site.

The repository includes a GitHub Actions workflow that:

1. builds the static site;
2. runs content and link validation;
3. uploads only the generated `dist/` site;
4. deploys the validated artifact to GitHub Pages.

The first review can use the repository's `github.io` address. After that works, configure `arsf.wonderfulrealms.com` in the repository's Pages settings and add the exact DNS record GitHub reports. Do not guess the record before the repository exists.

## Exact `/arsf` route

To serve the full prototype at `wonderfulrealms.com/arsf`, choose one of:

1. Put a routing layer such as Cloudflare in front of the domain and proxy only `/arsf/*` to the static host.
2. Move the Wonderful Realms site to hosting that supports path-based routing.
3. Create a GoDaddy `/arsf` page that links or redirects to the subdomain. This preserves a friendly entry URL but does not keep the final address at `/arsf`.

No DNS or hosting changes should be made until the prototype and public scope are approved.

## Production separation

The eventual ARSF production site should use ARSF-controlled domain, hosting, accounts, donation ownership, and editor access. The Wonderful Realms address is a review environment, not a permanent dependency.
