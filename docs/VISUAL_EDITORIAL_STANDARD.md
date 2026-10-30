# Visual editorial standard — Tech Tinkerer HQ

## Definition of Done for every published guide

The picture is a first-class part of the article, not decorative filler. A guide cannot move to `approved` until its individual visual is present, accurate enough for its topic, accessible, and reviewed by a human editor.

## Data schema (published article)

```json
"visual": {
  "src": "/assets/thumbnails/unique-topic-specific-name.webp",
  "alt": "Descriptive text describing exactly what the image depicts",
  "kind": "illustration"
}
```

- `src`: self-hosted under `assets/thumbnails/`; supported extensions: webp, png, jpg, avif.
- `alt`: concrete, subject-specific description (40–180 characters).
- `kind`: `illustration` or `verified-photo`.
- The path cannot be shared between different articles.
- The actual image file must be present in the repo and survive site QA.
- CI rejects referenced website thumbnail files smaller than 1000×500 pixels; reviewers must additionally detect blurry upscaled or overcompressed images by sight.
- AI-generated conceptual illustrations are labeled **Concept illustration** on cards and identified on the guide itself; they are **not** actual product photographs.
- Never add fabricated brand marks, impossible port counts, misleading product specifications, fake benchmark screenshots, or an unverified photo claiming to be an exact hardware model.

## State transitions and human review

`curated evidence → AI text draft (review_needed, no visual yet) → attach original relevant image asset → verify visual and factual claims → verified_by + sources_checked + visual_reviewed → approved → weekly publisher → Netlify`

Human sign-off must review the subject, legibility at card size, cropping, technical plausibility, alternative text, provenance/rights, and distinction between illustration versus manufacturer photography. A generic image or duplicated illustration is a rejection, even if the written article is good.

The weekly publisher refuses approved entries that lack `review.visual_reviewed=true`, usable visual metadata, or a real committed image asset. Static QA also refuses missing on-page image files. Neither AI drafting nor the website auto-approves a visual.

## Preferred image format

- Compose for the site's 2:1 card ratio; use a genuinely relevant subject for each article.
- The **original source** must be at least 1000×500 pixels; target 1200×600 or better for the 2:1 cards. Never create a 1200px output by enlarging a 200px thumbnail.
- Use full-resolution original assets and optimize final WebP quality/size without misleading upscaling claims. Verify the source dimensions **before** conversion.
- Keep useful details near the center for mobile crops.
- Use accessible contrast, no baked-in critical text, and avoid watermarks.
- Never load imagery from expiring CDN links in production. Commit permanent website assets.
- Update image alt text and article image if the article topic materially changes.

## Technical safeguards

The `src.schema` contract enforces the article-specific visual, unique image path, safe local path, a descriptive alt string, and a declared type. `scripts.weekly_release` requires the source file and explicit visual review. The builder copies `assets/`, and `src.qa` checks that all local `<img>` paths resolve. No generic card illustration fallback is allowed.
