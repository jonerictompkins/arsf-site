# Deployment options

## Current host finding

`wonderfulrealms.com` is served by GoDaddy Websites + Marketing. That product accepts custom-code sections, but it is not a general file host where this project can simply be uploaded into an `/arsf` directory.

## Recommended demo route

Use GitHub Pages at `arsf.wonderfulrealms.com`, matching the existing Wonderful Realms site-project pattern. This is isolated from the GoDaddy-managed main site, requires only a subdomain DNS record, and can later be removed without changing the main site.

The demo is now deployed at [arsf.wonderfulrealms.com](https://arsf.wonderfulrealms.com/). DNS validation has succeeded; GitHub Pages HTTPS enforcement can be enabled after certificate provisioning completes.

The repository includes a GitHub Actions workflow that:

1. builds the static site;
2. runs content and link validation;
3. uploads only the generated `dist/` site;
4. deploys the validated artifact to GitHub Pages.

The custom domain uses a CNAME from `arsf.wonderfulrealms.com` to the repository owner's GitHub Pages hostname. The site source and workflow remain independent of the GoDaddy-managed main website.

## Exact `/arsf` route

To serve the full prototype at `wonderfulrealms.com/arsf`, choose one of:

1. Put a routing layer such as Cloudflare in front of the domain and proxy only `/arsf/*` to the static host.
2. Move the Wonderful Realms site to hosting that supports path-based routing.
3. Create a GoDaddy `/arsf` page that links or redirects to the subdomain. This preserves a friendly entry URL but does not keep the final address at `/arsf`.

No path-based proxy or main-site hosting change is required for the current subdomain demo.

## Production separation

The eventual ARSF production site should use ARSF-controlled domain, hosting, accounts, donation ownership, and editor access. The Wonderful Realms address is a review environment, not a permanent dependency.
