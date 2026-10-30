# TechTinkerer HQ — Static Netlify Modernization

An evidence-first replacement of the original WordPress website. The old WordPress XML export is retained by its owner; it is **not** copied into the deploy or intended public GitHub repository.

## Definition of Done

1. Publish a modern mobile/desktop site with accessible guide search and three source-checked guides.
2. Validate all internal links, metadata, sitemap, robots, and legacy WordPress redirects.
3. Preserve the recovery export and original URLs without carrying forward unsupported product claims.
4. Connect a **new dedicated GitHub repository** to a Netlify staging site; verify the staging preview and domain/DNS records before cutover.
5. Publish production only after approval, cross-browser checks, and DNS/email preservation. Cancel **hosting only** after successful cutover, and retain domain/DNS/email services as necessary.

## Data schema (before functions)

`content/articles.json` has `schema_version=2` and a list of `articles` containing `id`, `slug`, `status`, `category`, `kind`, `reading_minutes`, `title`, `description`, `dek`, `sections[]`, and `sources[]`. Each section has `heading`, optional `paragraphs[]`, and optional `bullets[]`. Each evidence source has a human-readable `name` and HTTPS `url` on an allowlisted authoritative domain.

`archive/legacy-map.json` keeps old WordPress URLs and their destination route. No original WordPress email addresses or raw article bodies belong in the public repository.

## State logic

- `draft`: generated but never published.
- `research_needed`: claim lacks acceptable evidence; block.
- `review_needed`: evidence present but human review missing; block.
- `approved`: claims manually verified and source links present; can build.
- `preview`: built with `noindex`, `Disallow: /`, and a visible staging banner.
- `production`: only when explicit `RELEASE_APPROVED=true` is set **and** the build is invoked with `--mode production`. Never use production during initial setup.

Validation fails closed for any non-approved content, duplicate/unsafe slug, unsupported evidence domains, placeholder affiliate links, or bad legacy redirect.

## Local workflow

Requires Python 3.10+ (Netlify config requests 3.12); no pip packages needed.

```sh
python3 -m unittest discover -s tests -v
python3 -m src.builder --mode preview
python3 -m src.qa
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/` to inspect. The built-in Python server does not apply Netlify `_redirects`; test those after connecting Netlify.

## Deployment workflow

1. Create a dedicated repository in GitHub, e.g. `cbw29512/techtinkererhq`. Upload **the project contents**, not only `dist/`.
2. In Netlify, add a new project importing this repository. Netlify should read `netlify.toml` and build a noindex preview by default.
3. Test three guides, `/guides/` filters, internal links, 404, and the legacy 301 redirects on the Netlify staging domain.
4. Only after browser, SEO, accessibility, and DNS/email checks pass, coordinate domain migration and explicitly authorize a production-indexable build.

**Important:** SiteGround controls the current domain's nameservers in the owner's dashboard. Do not cancel hosting or change nameservers until the domain registrar, renewal, SSL, email/MX, and DNS responsibilities have been identified. Domain expiration shown: May 20, 2027.

## Remaining tasks

- Perform cross-browser tests and a real assistive-technology audit; automated checks alone do not certify ADA/WCAG conformance.
- Verify whether SiteGround hosts email or only WordPress; preserve DNS/mail records.
- Recover any actual original site uploads as a separate private archive, if present.
- Connect a GitHub repository and a Netlify project; neither exists for this site as of packaging.
- If an article bot is reintroduced, it must write reviewed, version-controlled article data, not publish directly from an LLM.
