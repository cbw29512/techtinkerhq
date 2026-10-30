# AI-generated article drafts — Definition of Done

## Objective

Automatically prepare **no more than one** documented technical article candidate
per week, but **never publish or approve it automatically**. This extends the existing
review queue and weekly publishing workflow. It is not a new website or CMS.

## Data schema (before implementation)

- `content/draft-topics.json`, `schema_version: 1`, contains curated `topics[]`.
- Each topic has stable `id`, URL-safe `slug`, `focus`, `category`, `kind`, an
  authoritative `sources[]` list, and `facts[]` (`id`, `text`).
- AI response has `title`, `description`, `dek`, `reading_minutes` and `sections[]`.
- Each section has `heading`, `paragraphs[]`, `bullets[]`, `evidence_ids[]`.
- The automation, not the AI, assigns source URLs, slug, category, state and review flags.
- Drafts enter `content/publish-queue.json` as `status: review_needed`,
  with blank human-review fields and their original evidence packet attached.

## State transitions

`curated topic → one structured model request → validated review_needed draft PR
→ human technical review → approved queue item → weekly publisher → Netlify`.

A draft PR has no production effect unless reviewed and merged. Even after its
merge, `review_needed` content does not appear on the public site. A reviewer
must verify claims, current model revisions, URLs, SEO and descriptions before
changing the queue status to `approved`. Never set both fields merely to make
CI pass. The original weekly publisher remains the only path to `articles.json`.

## Setup — disabled by default

1. In GitHub repo `cbw29512/techtinkerhq`, open **Settings → Secrets and
   variables → Actions**.
2. Add repository **secret** `OPENAI_API_KEY` from an OpenAI API account.
   Do not paste secrets into issue bodies, PRs or ChatGPT.
3. Add repository **variable** `OPENAI_DRAFT_MODEL` using a current model ID
   supported by Responses Structured Outputs, such as `gpt-5.5`. Confirm the
   model's availability and pricing in your API account before enabling.
4. Set a low monthly budget / usage alert in the OpenAI API dashboard. One
   model request is attempted per eligible scheduled run, with at most
   `3500` output tokens and a bounded input packet; fees depend on model.
5. Only after accepting API spending, add repository **variable**
   `ENABLE_AI_DRAFTS=true`. Without it, the GitHub job skips and spends zero.

## Operation and limitations

- `GitHub Actions → Draft source-grounded TechTinkerer guides` runs Tuesdays at
  15:23 UTC and supports manual runs. GitHub's schedule time is in UTC.
- Selects the next unused curated topic; with none left, does nothing.
- Skips a topic if its bot proposal branch already exists, preventing repeats.
- Sends *only* the curated fact packet and official source links to the model;
  there is **no independent live retrieval** in the current pilot.
- Uses OpenAI Responses Structured Outputs with `store=false` and no tools.
- Validates structure, evidence IDs, slugs, site source restrictions, and
  existing publishing schema; it cannot prove the facts are correct.
- Creates a proposed `review_needed` queue change in a GitHub pull request.
- GitHub Actions requires repository permission to create PRs. If PR creation
  is prohibited, the job fails and preserves the unapproved JSON as a downloadable
  Actions artifact; adjust repo Actions settings only if you choose.
- An Actions `GITHUB_TOKEN`-created PR may not trigger ordinary `pull_request`
  workflows. The draft job runs unit tests and site QA before opening its PR.
- Keep real publication gated by documented human review and weekly source QA.
- Source packets must be researched and refreshed; the AI cannot source its
  own claims or publish indefinite new articles with the current single seed.
