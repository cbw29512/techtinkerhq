# Migration cutover checklist

- [x] WordPress XML received and original post slugs cataloged (14 published posts, 1 published Sample Page).
- [x] Rewritten site built with 3 source-checked explanatory guides.
- [x] Duplicate and unverified imported posts excluded from the published article list.
- [x] 15 old routes mapped to new relevant routes (Netlify `_redirects`).
- [x] Local code/tests/metadata/internal links validated.
- [x] Staging deployment published at https://techtinkerhq.netlify.app/ (Netlify deploy `6ae4fd496484ccf5b50e28b9`, state `ready`, built from tested GitHub SHA `3e29e08cec558456a57be27a18f1d6dfea7214b8`).
- [ ] Verify HTTP 301 responses for legacy routes and HTTP 200 for all guide pages. Netlify confirms 15 redirect rules processed; initial edge logs confirm 200/304 for homepage, standards, and CSS, but do not yet verify all routes.
- [ ] Manual keyboard/screen-reader and mobile/browser QA.
- [ ] Verify ownership and renewal of `techtinkererhq.com`, plus SiteGround DNS records and possible email MX/SPF/DKIM.
- [ ] Confirm SSL issuance and domain binding at Netlify.
- [ ] Written production approval and production SEO indexing change.
- [ ] Domain cutover; observe DNS and SSL before terminating WordPress hosting.
- [ ] Cancel only unneeded SiteGround hosting after verified live site and backup retention.

**Do not cancel SiteGround based on build success alone.** The current SiteGround hosting and domain dashboard both show expiration on May 20, 2027.
