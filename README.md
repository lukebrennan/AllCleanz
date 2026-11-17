# All Cleanz Website

New landing page for [All Cleanz](https://www.allcleanz.co.uk/), a domestic and commercial cleaning company based in Merseyside, working across the North West.

A static site: plain HTML, CSS and JavaScript with no build step.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Homepage: hero with call/WhatsApp CTAs, about, 14 services, Texatherm carpet cleaning, why choose us, clients, testimonials, quote form |
| 14 service pages, e.g. `end-of-tenancy-cleaning.html`, `oven-cleaning.html`, `bbq-cleaning.html` | One page per service, copy taken from the matching page on the old Wix site. Each has its own title, description, canonical URL and `Service` + `BreadcrumbList` JSON-LD |
| `services.html` | All 14 services in one grid |
| `about.html` | About copy, clients and testimonials |
| `areas-we-cover.html` and `cleaners-*.html` (Whiston, Rainhill, Huyton, St Helens, Kirkby, Widnes, Liverpool, Warrington) | Location pages. Prescot deliberately has no page of its own: the homepage targets "cleaners prescot", and a second page would compete with it. Each town page has its own local copy, nearby areas, FAQs (with `FAQPage` schema) and straight-line distance from Prescot. **To add or turn off a town**, add or delete its entry in `LOCATIONS` in `tools/build_pages.py` and re-run the build: the page, the homepage Areas links, the Areas page card, the sitemap and `llms.txt` all update. If a removed page was already live, add a 301 from it to `/areas-we-cover` in `netlify.toml` |
| `join-the-team.html` | Job application form (domestic cleaner, cleaning supervisor, car valeter) |
| `our-work.html` | Gallery of the client's before and after photos: driveways and patios, ovens, gutters, carpets and stairs |
| `faq.html` | 23 FAQs in six groups, with `FAQPage` schema. Every answer uses the business's own published wording (old website, Google listing). Five of them also appear on the homepage, generated from the same list (`FAQ_GROUPS` and `HOME_FAQ_QS` in `tools/build_pages.py`). Prices, opening hours, insurance, DBS checks and payment methods are deliberately not answered until the client confirms them |
| `review.html` | "Leave us a review" page with a button and QR code that open the All Cleanz Google review form. `noindex`, not in the sitemap; linked from the footer |
| `404.html` | Not found page |

Pages are linked without `.html` (e.g. `/oven-cleaning`). The header and footer are copied from `index.html` into every page, so a change to either needs making on all pages. Clients and Testimonials in the menu link to those sections of the homepage.

## Editing pages

Every page except the homepage is generated, so edits go through the build scripts:

1. Change the header, footer or a shared homepage section (why choose us, clients, testimonials, services grid) in `index.html`, or a page's copy in `tools/build_pages.py`.
2. Run `python3 tools/build_pages.py . <version>`, where `<version>` is the `?v=` value for `styles.css` and `main.js` (e.g. `20261116-1`). Bump it whenever either file changes.
3. Run `python3 tools/build_llms_full.py .` to refresh `llms-full.txt`.
4. Add any new page to `sitemap.xml` and `llms.txt`.

`404.html` is not generated: copy header or footer changes into it by hand.

## Print materials (`print/`)

Not part of the website (hidden on Netlify at launch):

- `review-card.pdf` / `.png`: A6 thank-you card with a QR code to the Google review form, ready to print or send on WhatsApp. Edit `review-card.html` and re-render with Playwright if the wording changes.
- `review-qr.png` / `.svg`: the review QR code on its own (for business cards, van stickers, invoices)
- `website-qr.png`: QR code for https://www.allcleanz.co.uk/

The review link is `https://search.google.com/local/writereview?placeid=ChIJE3yGEImFwWURhPb_ciz941g`, built from the Google Business Profile's place ID.

## Structure

```
assets/
  css/styles.css      Brand tokens (green #43B288), layout, responsive rules
  js/main.js          Mobile menu, services dropdown, scroll reveal, ticker, quote and job application forms, before/after slider, lead tracking
  img/                Logo variants, favicons, photos (WebP)
  img/services/       Service card photos
robots.txt, sitemap.xml, site.webmanifest
```

## Content

All copy, services, claims and testimonials are taken from the existing allcleanz.co.uk site. Nothing has been invented.

Photos: almost all photos are All Cleanz's own, taken from their Facebook page (downloaded at the highest resolution Facebook serves). This includes the hero, the about section, the before and after slider, the recent work strip and the main service cards. Photos sent by the client (November 2026) are used for Jet Washing (hero, two before/after sliders, a before/after pair and patio photos), Gutter Cleaning (the high reach gutter vacuum and a fascia before/after) and a carpet cleaning gallery; these live in `assets/img/work/`. The Deep Cleaning card and a few others (office, after build, party, window, car valeting and BBQ cleaning) still use the images from their previous website.

## SEO

- Title and meta description targeting "cleaning company Merseyside / North West"
- `WebSite`, `WebPage` and `LocalBusiness` JSON-LD (phone, email, area served, Google Maps listing, all 14 services linked to their pages); each page has `WebPage` + `BreadcrumbList`, service pages add `Service`, the Services page an `ItemList`. Validated with validator.schema.org
- Open Graph tags, canonical URL, sitemap and robots.txt
- Fonts (Inter and Poppins, Latin subset) are self-hosted in `assets/fonts/` and the hero fonts are preloaded, so no third-party requests block rendering
- Semantic headings (single H1), descriptive image alt text, lazy-loaded below the fold images, WebP images
- 1200x630 social sharing image (`assets/img/og-image.jpg`). During the preview, the `og:image` and `twitter:image` tags point at the GitHub Pages copy so link previews work; switch them back to `https://www.allcleanz.co.uk/assets/img/og-image.jpg` at launch
- `llms.txt` summary for AI assistants and search tools, and `llms-full.txt` with the text of every page (regenerate it when page copy changes)
- `robots.txt` and `sitemap.xml` (with image entries) point at the final domain, www.allcleanz.co.uk

## Launch checklist (SEO)

1. Remove the preview passcode (see below) and switch `og:image` / `twitter:image` back to the www.allcleanz.co.uk address on every page.
2. Point the domain at the new host. `netlify.toml` handles the old Wix redirects.
3. Google Search Console: verify the domain (DNS record), submit `https://www.allcleanz.co.uk/sitemap.xml`, and use URL Inspection to request indexing of the homepage and service pages.
4. Bing Webmaster Tools: import the site from Search Console and submit the sitemap.
5. IndexNow (Bing, Yandex and others): the key file `1114069adc60dde094b24bb030937154.txt` is in the site root. After launch, and whenever pages change, submit the URLs:
   `https://api.indexnow.org/indexnow?url=https://www.allcleanz.co.uk/&key=1114069adc60dde094b24bb030937154`
6. Google Business Profile: set the website to `https://www.allcleanz.co.uk/` and check the name, phone and service area match the site.
7. Test the homepage and a service page in Google's Rich Results Test and the Schema Markup Validator.
8. Watch Search Console's Pages report for 404s over the first few weeks.

## Launch settings (`netlify.toml`)

Ignored by GitHub Pages, active once the site is on Netlify:

- 301 redirects from the old Wix URLs (e.g. `/end-of-tenancy-1`) to the matching new page or homepage section, so Google rankings carry over
- Redirect from `allcleanz.co.uk` to `www.allcleanz.co.uk`
- Long browser caching for CSS, JS and fonts (bump the `?v=` value on every page when `styles.css` or `main.js` changes), 30 days for images
- Standard security headers

## Lead tracking

`main.js` sends events for phone clicks (`click_call`), WhatsApp clicks (`click_whatsapp`), email clicks (`click_email`) quote form submissions (`quote_form_submit`) and job applications (`join_form_submit`), with where on the page the click happened. Nothing is sent until Google Analytics 4 (`gtag`) or Plausible is added to the pages; it then picks them up automatically. GA4 needs a cookie consent banner in the UK; Plausible does not.

## Hosting

Preview site (GitHub Pages, built from `main`): https://lukebrennan.github.io/AllCleanz/

The production host (Netlify, `allcleanz.netlify.app`) is paused until launch.

## Forms

**Join the Team form:** marked up for Netlify Forms (`data-netlify`, honeypot, CV upload). For now `main.js` stops the real submit and hands the application to a pre-filled email or WhatsApp message, so nothing is lost before launch. Once Netlify Forms is switched on, remove that hand-off in `main.js` so the form posts normally.

**Quote form:** the quote form (in the contact section) is a demo: it walks through service, property, frequency and contact details, then shows a summary. It does not send anything to an inbox yet, so connect it (for example with Netlify Forms) before launch. The confirmation screen's "Send these details on WhatsApp" button does work, as do the pre-filled WhatsApp links across the site.

## Preview passcode

While the site is in preview, every page shows a branded passcode screen (`assets/js/gate.js`, plus a one-line script at the top of each page's `<head>`). The passcode is not case sensitive. Once entered, the browser remembers it.

This is a deterrent, not real security: the page content is still delivered to the browser and the repository is public. Remove the gate before launch.

## Run locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000. Pages are linked without `.html`, which GitHub Pages and Netlify handle; with this simple server, add `.html` to the address.
