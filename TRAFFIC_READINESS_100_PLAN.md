# WC2026 Site - 100% Traffic Readiness Plan

**Project:** World Cup 2026 / worldcup-site  
**Live domain:** https://wc2026.ehabkhedr.com  
**Roadmap item:** WC-0013  
**Track:** Private Business  
**Plan date:** 2026-06-19  
**Current score:** 68/100  
**Target score:** 100/100 traffic readiness before aggressive distribution

---

## 1. Project Objective

Turn `wc2026.ehabkhedr.com` from a working MVP into a real-world traffic-ready World Cup site that can safely handle fast social/search growth.

This project must improve nine readiness categories:

| Category | Current | Target | Main Gap |
|---|---:|---:|---|
| 1. Availability and Deployment | 92 | 100 | Needs repeatable Cloudflare-first release checks |
| 2. Performance and Cache | 78 | 100 | HTML is not edge-cached effectively |
| 3. Desktop UX | 82 | 100 | Good baseline, needs polish and stronger navigation states |
| 4. Mobile UX | 55 | 100 | Header/nav clips on mobile |
| 5. SEO and Indexing | 46 | 100 | Canonicals, H1s, sitemap URLs, structured data |
| 6. Social Sharing | 40 | 100 | `og-image.jpg` is not a real image |
| 7. Content Authority | 74 | 100 | Needs hub pages, freshness, model accuracy proof |
| 8. Monetization | 45 | 100 | CTAs exist but funnel is weak and untracked |
| 9. Growth Instrumentation | 25 | 100 | No analytics, campaign tagging, or index pipeline verification |

---

## 2. Folder Ownership

Work from the source-side project folder:

```text
projects/world-cup-2026/site/
```

Primary files:

| File | Role |
|---|---|
| `build.py` | Static generator, page templates, metadata, sitemap, robots, headers |
| `site-data/matches.json` | Match schedule and status source |
| `site-data/groups.json` | Group standings source |
| `site-data/predictions.json` | Prediction source |
| `site-data/reviews.json` | Review source |
| `worldcup-site/` | Generated output for Cloudflare Pages |
| `wrangler.toml` | Cloudflare Pages project config |

Do not manually patch generated HTML in `worldcup-site/` except for emergency diagnosis. Fix generator/source files, rebuild, then verify output.

---

## 3. Execution Strategy

The fastest path to 100 is three waves:

| Wave | Goal | Timebox | Result |
|---|---|---:|---|
| Wave 1 | Fix trust blockers | 4-6 hours | Search engines and social platforms see correct page identity |
| Wave 2 | Fix UX and speed | 4-6 hours | Mobile/social users can browse without clipping or friction |
| Wave 3 | Add growth engine | 1-2 days | Traffic is measurable, repeatable, and monetizable |

Do not push heavy traffic until Wave 1 and Wave 2 pass.

---

## 4. Wave 1 - Search and Social Trust Blockers

### 4.1 Per-page canonical and `og:url`

**Problem:** Most non-home pages canonicalize to the homepage. This can collapse match pages in search.

**Implementation:**

1. Change `page_head()` call sites to pass a route-specific canonical path.
2. Add helper:

```python
def canonical_path(path):
    if path == "/":
        return "/"
    return path if path.endswith("/") else path
```

3. Required canonical examples:

| Page | Canonical |
|---|---|
| Home | `https://wc2026.ehabkhedr.com/` |
| Matches index | `https://wc2026.ehabkhedr.com/matches/` |
| Match page | `https://wc2026.ehabkhedr.com/matches/wc2026-grp-c-3` |
| Review page | `https://wc2026.ehabkhedr.com/reviews/wc2026-grp-a-1` |

**Acceptance:**

- `curl -s https://wc2026.ehabkhedr.com/matches/wc2026-grp-c-3 | rg 'canonical|og:url'` shows that exact URL.
- Crawl shows `CANONICAL_TO_ROOT_COUNT 0`, except homepage itself.

### 4.2 Sitemap final URLs

**Problem:** Sitemap contains `.html` URLs while live routes redirect to extensionless URLs.

**Implementation:**

1. Generate sitemap URLs as final extensionless URLs.
2. Internal links should also use final extensionless URLs.
3. Keep redirects from `.html` to extensionless for old links.

**Acceptance:**

- Sitemap includes `/matches/wc2026-grp-c-3`, not `/matches/wc2026-grp-c-3.html`.
- No sitemap URL returns 3xx.
- Google canonical signals match: internal links, canonical tags, sitemap URLs.

### 4.3 Real OpenGraph image

**Problem:** `/og-image.jpg` returns HTML, not an image.

**Implementation:**

1. Create a real `1200x630` default OG image at `worldcup-site/og-image.jpg`.
2. Add a generator path for per-match images later:
   - `/og/matches/{match_id}.jpg`
   - `/og/reviews/{match_id}.jpg`
3. For now, all pages can use a valid default image.

**Acceptance:**

- `curl -I https://wc2026.ehabkhedr.com/og-image.jpg` returns `content-type: image/jpeg`.
- X/Twitter and Facebook debuggers show a large image preview.

### 4.4 H1 coverage

**Problem:** Many index and generated pages lack a real H1.

**Implementation:**

1. Ensure exactly one visible H1 on each page.
2. Use H1s that match search intent:
   - `World Cup 2026 AI Predictions`
   - `World Cup 2026 Matches`
   - `{Home Team} vs {Away Team} Prediction`
   - `{Home Team} vs {Away Team} Review`

**Acceptance:**

- Crawl reports `MISSING_H1_COUNT 0`.
- No page has more than one H1.

### 4.5 Structured data

**Implementation:**

1. Keep `WebSite` schema on homepage.
2. Add `BreadcrumbList` schema to all non-home pages.
3. Add `SportsEvent` schema to individual match pages.
4. Add `Article` or `Review`-style schema only where the visible page content supports it.

**Acceptance:**

- JSON-LD validates as parseable JSON.
- Rich Results Test has no critical structured data errors.

---

## 5. Wave 2 - UX, Accessibility, and Performance

### 5.1 Mobile header and navigation

**Problem:** Mobile header wraps/clips and nav can overflow.

**Implementation:**

1. Replace one-line header flex with a responsive layout:
   - desktop: logo left, nav right
   - tablet/mobile: logo row, horizontal scroll nav row
2. Add `overflow-x:auto` for nav, stable tap targets, and no text clipping.
3. Keep nav visible without covering content.

**Acceptance:**

- Viewports pass: 390x844, 430x932, 768x1024, 1440x900.
- No header/nav clipping.
- First content remains visible under sticky header.

### 5.2 Filter controls as buttons

**Problem:** Match filters are `div` elements with inline `onclick`.

**Implementation:**

1. Replace filters with `<button type="button">`.
2. Add `aria-pressed`, keyboard focus style, and event listener binding.
3. Avoid relying on global `event`.

**Acceptance:**

- Keyboard users can Tab to each filter and activate with Enter/Space.
- Console has no errors after filter clicks.

### 5.3 Desktop UX polish

**Implementation:**

1. Add active nav state for current route.
2. Improve match cards with clearer date/time hierarchy.
3. Add "today", "tomorrow", and "next match" sections on homepage.
4. Add breadcrumbs on deep pages.

**Acceptance:**

- User can reach any core page in one click from header.
- Match pages link back to matches, group, and predictions pages.

### 5.4 Cloudflare caching

**Problem:** Live HTML is `max-age=0` / dynamic, so traffic spikes will hit origin more than needed.

**Implementation:**

1. Update generated `_headers` to target extensionless routes, not only `/*.html`.
2. Add Cloudflare cache rules for HTML:
   - match pages: cache 5-10 minutes, stale while revalidate
   - static assets: cache 30 days to 1 year with immutable filenames
   - sitemap/robots/llms: cache 1 hour to 1 day
3. Ensure no route sets cookies.

**Acceptance:**

- `curl -I https://wc2026.ehabkhedr.com/matches/wc2026-grp-c-3` shows positive `Cache-Control`.
- Repeat request shows Cloudflare cache HIT or eligible cache behavior.

### 5.5 Core Web Vitals targets

**Targets:**

| Metric | Target |
|---|---:|
| LCP | <= 2.5s |
| INP | <= 200ms |
| CLS | <= 0.1 |
| TTFB | <= 800ms |

**Implementation:**

1. Keep pages static and dependency-free.
2. Remove unused preconnect to Pages preview domain if no live requests use it.
3. Add dimensions to images.
4. Keep JS tiny and route-local.
5. Run Lighthouse/PageSpeed after deployment.

**Acceptance:**

- Mobile Lighthouse performance >= 90.
- No critical render-blocking third-party scripts.

---

## 6. Wave 3 - Content, Monetization, and Growth Engine

### 6.1 Content authority upgrades

**Implementation:**

1. Add team profile pages for all teams.
2. Add group landing pages:
   - `/groups/group-a`
   - `/groups/group-b`
3. Add model accuracy leaderboard:
   - exact score accuracy
   - outcome accuracy
   - average goal difference error
4. Add daily matchday hub:
   - `/today`
   - `/tomorrow`
   - `/latest-reviews`

**Acceptance:**

- Site grows from 84 pages to at least 150 useful pages.
- Each new page has unique title, description, H1, canonical, and internal links.

### 6.2 Monetization funnel

**Implementation:**

1. Replace generic CTAs with route-specific CTAs:
   - match page: merch collection for the teams/match theme
   - predictions page: AI business automation CTA
   - reviews page: subscribe/follow CTA
2. Add a small lead capture option only if Ehab approves the destination.
3. Add UTM parameters to social/shared links.
4. Keep betting/affiliate links out until legal review is complete.

**Acceptance:**

- Every core page has one primary CTA and one secondary CTA.
- CTAs are tracked separately by source/page.
- No official FIFA/team/player IP is used in merch messaging.

### 6.3 Analytics and campaign tracking

**Implementation:**

1. Enable Cloudflare Web Analytics on the Pages project.
2. Add a lightweight event plan:
   - page view
   - outbound merch click
   - business CTA click
   - social source campaign
3. Use UTM rules for every tweet/social link:
   - `utm_source=x`
   - `utm_medium=social`
   - `utm_campaign=wc2026_matchday`
   - `utm_content={match_id}_{post_type}`

**Acceptance:**

- Dashboard shows visits by route and referrer.
- Outbound CTA clicks are measurable.
- Every queued social post uses a campaign-tagged URL.

### 6.4 Indexing pipeline

**Implementation:**

1. Submit sitemap in Google Search Console.
2. Submit sitemap in Bing Webmaster Tools.
3. Add IndexNow for changed/new URLs.
4. Keep robots.txt simple and non-contradictory.
5. Recheck Cloudflare Managed content signals so AI bot rules do not conflict with local robots goals.

**Acceptance:**

- Search Console sitemap status is success.
- Bing sitemap status is success.
- IndexNow returns successful submission for changed URLs.

### 6.5 Traffic launch system

**Implementation:**

1. Build 3 daily content loops:
   - pre-match predictions
   - live/today match hub
   - post-match review and model accuracy
2. Cross-link every social post to a specific canonical page, not only homepage.
3. Create daily scorecard:
   - visits
   - top pages
   - CTR from social
   - merch clicks
   - business CTA clicks
   - indexed pages

**Acceptance:**

- Daily traffic report can be produced in under 10 minutes.
- Top-performing pages are fed back into tweet/content planning.

---

## 7. Implementation Backlog

| ID | Task | Category | Priority | Owner | Estimate | Done When |
|---|---|---|---|---|---:|---|
| WC100-01 | Fix per-page canonical and `og:url` | SEO | P0 | Codex/Hermes | 1h | 0 pages canonicalize to root incorrectly |
| WC100-02 | Generate extensionless sitemap URLs | SEO | P0 | Codex/Hermes | 45m | Sitemap URLs return 200, no 3xx |
| WC100-03 | Add real `og-image.jpg` | Social | P0 | Antigravity/Codex | 1h | Image returns JPEG/PNG content type |
| WC100-04 | Add one H1 per generated page | SEO/UX | P0 | Codex/Hermes | 1h | Missing H1 count is 0 |
| WC100-05 | Add BreadcrumbList and SportsEvent JSON-LD | SEO | P1 | Codex/Hermes | 2h | Structured data parses cleanly |
| WC100-06 | Fix mobile nav/header layout | Mobile UX | P0 | Codex | 2h | 390px viewport has no clipping |
| WC100-07 | Replace filter divs with buttons | Accessibility | P1 | Codex | 1h | Keyboard + click both work |
| WC100-08 | Update Cloudflare `_headers` and cache rules | Performance | P0 | Codex/Ehab | 1h | HTML has positive cache TTL |
| WC100-09 | Add analytics and UTM rules | Growth | P0 | Ehab/Codex | 1h | Visits and CTA clicks measurable |
| WC100-10 | Add route-specific CTAs | Monetization | P1 | Codex/Scribe | 2h | Every route has tracked CTA |
| WC100-11 | Add team/group/day hub pages | Content | P2 | Scribe/Hermes | 1d | 150+ useful indexable pages |
| WC100-12 | Add model accuracy leaderboard | Content/Trust | P1 | Hermes/Codex | 4h | Accuracy page updates from data |
| WC100-13 | Search Console/Bing/IndexNow setup | Growth | P1 | Ehab/Codex | 2h | Sitemap and changed URLs submitted |
| WC100-14 | Browser QA matrix | QA | P0 | Codex | 1h | Desktop/mobile screenshots pass |
| WC100-15 | Launch traffic playbook | Growth | P1 | Swift/Scribe | 2h | Daily posting links to canonical pages |

---

## 8. Definition of 100%

The site reaches 100/100 only when all of these are true:

1. Live domain and all sitemap URLs return 200 without unexpected redirects.
2. Every page has correct title, description, canonical, `og:url`, and one H1.
3. `/og-image.jpg` is a real image and social cards render correctly.
4. Mobile header and navigation do not clip at 390px width.
5. Match filters are semantic, accessible buttons.
6. HTML routes are edge-cache eligible on Cloudflare.
7. Core Web Vitals targets are met on mobile and desktop.
8. Analytics is enabled and social links use UTMs.
9. CTAs are specific, tracked, and legally safe.
10. Sitemap is submitted and clean in Google/Bing.
11. Daily content and review loops are repeatable.
12. No secrets, private credentials, or proprietary business logic are exposed.

---

## 9. QA Checklist

Run after every deployment:

```bash
python3 build.py
find worldcup-site -name '*.html' | wc -l
curl -I https://wc2026.ehabkhedr.com/
curl -I https://wc2026.ehabkhedr.com/matches/
curl -I https://wc2026.ehabkhedr.com/matches/wc2026-grp-c-3
curl -I https://wc2026.ehabkhedr.com/og-image.jpg
curl -s https://wc2026.ehabkhedr.com/sitemap.xml | head
```

Browser QA:

| Viewport | Pages |
|---|---|
| 390x844 | Home, matches, match page |
| 430x932 | Home, matches |
| 768x1024 | Home, matches, groups |
| 1440x900 | Home, matches, predictions, review |

Automated checks:

- Canonical mismatch count
- Missing H1 count
- Duplicate title count
- Duplicate description count
- Sitemap non-200 count
- Console error/warning check
- Social image content-type check
- Cache header check

---

## 10. Source Notes

Planning follows current official guidance:

- Google canonical guidance: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Google structured data guidance: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- Google BreadcrumbList guidance: https://developers.google.com/search/docs/appearance/structured-data/breadcrumb
- Google Core Web Vitals guidance: https://developers.google.com/search/docs/appearance/core-web-vitals
- web.dev Web Vitals thresholds: https://web.dev/articles/vitals
- Cloudflare Pages `_headers`: https://developers.cloudflare.com/pages/configuration/headers/
- Cloudflare cache behavior: https://developers.cloudflare.com/cache/concepts/default-cache-behavior/
- Cloudflare Web Analytics: https://developers.cloudflare.com/pages/how-to/web-analytics/

---

## 11. Recommended Next Build Order

1. `WC100-01` canonical/og:url
2. `WC100-02` sitemap final URLs
3. `WC100-03` real OG image
4. `WC100-06` mobile header/nav
5. `WC100-04` H1 coverage
6. `WC100-08` Cloudflare cache rules
7. `WC100-07` accessible filter buttons
8. `WC100-09` analytics/UTMs
9. `WC100-10` monetization CTA tracking

This order removes the main traffic blockers first, then makes the traffic useful.
