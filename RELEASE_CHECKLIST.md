# Migration cutover checklist

- [x] WordPress XML received and original post slugs cataloged (14 published posts, 1 published Sample Page).
- [x] Rewritten site built with 3 source-checked explanatory guides.
- [x] Duplicate and unverified imported posts excluded from the published article list.
- [x] 15 old routes mapped to new relevant routes (Netlify `_redirects`).
- [x] Local code/tests/metadata/internal links validated.
- [x] Staging deployment published at https://techtinkerhq.netlify.app/ (Netlify deploy `6ae4fd496484ccf5b50e28b9`, state `ready`, built from tested GitHub SHA `3e29e08cec558456a57be27a18f1d6dfea7214b8`).
- [ ] Verify HTTP 301 responses for legacy routes and HTTP 200 for all guide pages. Netlify confirms 15 redirect rules processed; initial edge logs confirm 200/304 for homepage, standards, and CSS, but do not yet verify all routes.
- [ ] Manual keyboard/screen-reader and mobile/browser QA.
- [x] Registrar/renewal verified at SiteGround (expires May 20, 2027). Owner confirmed DNS: apex A 75.2.60.5; www CNAME techtinkerhq.netlify.app. Separate mail/SSH/FTP and MX/SPF/DKIM/DMARC records preserved.
- [x] Owner reported successful DNS verification in Netlify on October 30, 2026; certificate issuance and end-to-end HTTPS still require verification.
- [ ] Confirm SSL issuance and domain binding at Netlify.
- [x] Production-context SEO build prepared in `netlify.toml`; previews remain `noindex`. Approval to launch was given by owner, but do not merge the production switch until SSL and custom-domain response are verified.
- [ ] Confirm apex HTTPS 200 and www HTTPS redirect, canonical/indexable meta, robots.txt, sitemap.xml, all three guide pages, and legacy redirects on the actual custom domain. Do not cancel SiteGround before verifying hosted mail services and backup retention.
- [ ] Cancel only unneeded SiteGround hosting after verified live site and backup retention.

**Do not cancel SiteGround based on build success alone.** The current SiteGround hosting and domain dashboard both show expiration on May 20, 2027.
