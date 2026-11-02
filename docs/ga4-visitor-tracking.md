# NucDash GA4 website visitors — first verified rollout

## Objective and source

GA4 account: `NucDash Websites`; shared property: `NucDash Website Traffic`.
Public measurement ID: `G-SMB3Q8QMJ5`. First website: `techtinkererhq.com`.

Measurement ID is **public configuration**, not a service-account key, token or secret.

## Data schema and state before implementation

- Browser consent state: `undecided | accepted | declined`; stored per-origin
  under `tthq_ga4_consent_v1`, never submitted to GitHub or NucBox.
- On `undecided` or `declined`: Google tag is not loaded; no GA4 data is sent.
- On `accepted`: dynamic `gtag.js` loads, basic Consent Mode v2 sets
  `analytics_storage=granted` and keeps advertising consent denied.
- Changing to `declined` disables future collection, clears known GA cookies,
  and reloads to remove the already-loaded Google script.
- Previews do not embed any analytics tag or banner.
- No change to SEO, redirects, visuals, domains or existing deployment gates.

## Report semantics

Query the GA4 Data API dimension `hostName` and metrics `totalUsers`,
`screenPageViews`; rank only recognized hostname-to-site mappings.
Use full seven completed days for ranking, compare with previous seven.
Use `null` when property access, a site mapping or a period is unavailable;
never invent zero and never label edge requests as visitors.

`totalUsers` reflects **tracked users**, not every real human visit.
Users blocking measurement or declining consent may not be counted.
Cross-domain aggregation is a shared reporting convenience, not a substitute
for isolated GA4 properties for unrelated business data.

## Verification gates

1. Tests and preview generator pass, and preview HTML contains no GA4 tag.
2. Production build contains exactly one GA4 loader on each generated page.
3. Netlify production Content-Security-Policy permits only needed Google endpoints.
4. After *explicit production approval*, verify Netlify deployment and test
   Google Analytics Realtime while consenting on techtinkererhq.com.
5. Confirm hostname matches the real site, not an unapproved preview domain.
6. Only then roll out to other websites and configure the NucBox reader.

Review privacy/legal requirements for each website and territory before rollout.
Do not commit OAuth credentials, service-account JSON or API tokens.
