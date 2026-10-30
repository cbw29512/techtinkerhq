# Migration cutover checklist

- [x] WordPress XML received and original post slugs cataloged (14 published posts, 1 published Sample Page).
- [x] Rewritten site built with 3 source-checked explanatory guides.
- [x] Duplicate and unverified imported posts excluded from the published article list.
- [x] 15 old routes mapped to new relevant routes (Netlify `_redirects`).
- [x] Local code/tests/metadata/internal links validated.
- [ ] External staging deployment at a Netlify subdomain.
- [ ] Verify HTTP responses for old routes and all new routes in staging.
- [ ] Manual keyboard/screen-reader and mobile/browser QA.
- [ ] Verify ownership and renewal of `techtinkererhq.com`, plus SiteGround DNS records and possible email MX/SPF/DKIM.
- [ ] Confirm SSL issuance and domain binding at Netlify.
- [ ] Written production approval and production SEO indexing change.
- [ ] Domain cutover; observe DNS and SSL before terminating WordPress hosting.
- [ ] Cancel only unneeded SiteGround hosting after verified live site and backup retention.

**Do not cancel SiteGround based on build success alone.** The current SiteGround hosting and domain dashboard both show expiration on May 20, 2027.
