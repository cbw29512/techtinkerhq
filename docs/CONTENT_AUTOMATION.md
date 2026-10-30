# Weekly content publishing — Definition of Done and data contract

## Objective

TechTinkerer HQ should release **at most one approved technical guide each Monday**
without manual copying, FTP, WordPress, or Netlify uploads. It must not automatically
approve claims, invent product tests, or publish unreviewed articles.

## Data schema

- `content/articles.json`: existing `schema_version: 2` public approved guides.
- `content/publish-queue.json`: `schema_version: 1` and ordered `items[]`.
- Each queue item: `id`, `slug`, `status`, `review`, `article`.
- `article` uses the same fields as public articles: `id`, `slug`, `status`,
  `title`, `description`, `dek`, `category`, `kind`, `reading_minutes`,
  `featured`, `sections[]`, and `sources[]`.
- Each `sources[]` entry has `name` and authoritative HTTPS `url`.
- Review has `verified_by`, `verified_at` (YYYY-MM-DD) and `sources_checked`.

## State transitions

1. `review_needed` — source-backed editorial candidate; NEVER publishes.
2. Human checks each material specification against the linked current source;
   fixes the article, makes `status: approved`, fills the review fields.
3. Scheduled workflow selects the first approved queue entry. It checks that
   review fields exist and that the slug is not already published.
4. Validator reads proposed article content using the existing site schema.
   The workflow builds the site, runs unit tests and static-site QA.
5. Only after every check succeeds does GitHub commit the article and mark
   the queue item `published`.
6. Netlify's existing Git connection sees the main-branch update and rebuilds
   the staging site. Staging remains noindex.
7. On any failure, the workflow stops without a commit. No article is deployed.

## Cadence and operation

- GitHub Actions workflow: `.github/workflows/weekly-content.yml`.
- Scheduled Mondays at **14:17 UTC** (09:17 EST or 10:17 EDT).
- Manual run: GitHub → Actions → Publish one reviewed TechTinkerer guide weekly
  → Run workflow.
- Queue input: edit `content/publish-queue.json` in a pull request, review, and
  merge the approved queue entry. Do not commit unreviewed claims with `approved`.
- The queue currently contains a Proxmox bridge/VLAN draft requiring editorial approval.
- The process needs NO paid AI API key to publish an already approved queue entry.
- It does NOT research new topics or write new articles by itself yet.

## Release safeguards

- No placeholders, fabricated personal testing, unapproved evidence hosts, or
  unverified affiliate purchase links are accepted by `src/schema.py`.
- Duplicate slugs and queue/archive mismatches block the job.
- CI tests the approved release path, re-runs do not duplicate publication, and
  the workflow publishes only one queued article per scheduled invocation.
- The source review remains a **human assertion**, not an independently
  guaranteed factual verification of every claim.
- On the current site, all Git builds remain noindex until domain cutover is
  explicitly approved and the production build configuration is changed.

## Future AI-writing stage (not activated)

Add a separate draft-generating job only after selecting an API provider,
configuring its secret, grounding proposed facts in retrieved authoritative
source text, and adding citations and checks. Generated output MUST enter
`review_needed`, never `approved`. ChatGPT subscriptions do not include
automatic API use.
