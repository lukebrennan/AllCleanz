# All Cleanz Website

New landing page for [All Cleanz](https://www.allcleanz.co.uk/), a domestic and commercial cleaning company based in Merseyside, working across the North West.

A static site: plain HTML, CSS and JavaScript with no build step.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Landing page: hero with call/WhatsApp CTAs, about, 14 services, Texatherm carpet cleaning, why choose us, clients, testimonials, contact |
| `end-of-tenancy-cleaning.html`, `deep-cleaning.html`, `domestic-cleaning.html`, `carpet-upholstery-cleaning.html`, `office-cleaning.html`, `oven-cleaning.html` | Service pages, linked without `.html` (e.g. `/oven-cleaning`). Copy is from the matching page on the old Wix site. Each has its own title, description, canonical URL and `Service` + `BreadcrumbList` JSON-LD. The header and footer are copied from `index.html`, so change all pages when editing them |
| `under-construction.html` | Target for the remaining nav links. Reads `?page=<slug>` to show which page was requested. `noindex` |
| `404.html` | Not found page for static hosts such as GitHub Pages or Netlify |

## Structure

```
assets/
  css/styles.css      Brand tokens (green #43B288), layout, responsive rules
  js/main.js          Mobile menu, services dropdown, scroll reveal, ticker, under construction labels
  img/                Logo variants, favicons, photos (WebP)
  img/services/       Service card photos
robots.txt, sitemap.xml, site.webmanifest
```

## Content

All copy, services, claims and testimonials are taken from the existing allcleanz.co.uk site. Nothing has been invented.

Photos: almost all photos are All Cleanz's own, taken from their Facebook page (downloaded at the highest resolution Facebook serves). This includes the hero, the about section, the before and after slider, the recent work strip and the main service cards. The Deep Cleaning card and a few others (office, after build, party, window, car valeting, jet washing, gutter and BBQ cleaning) still use the images from their previous website, as their Facebook has no clear photos of those services yet.

## SEO

- Title and meta description targeting "cleaning company Merseyside / North West"
- `WebSite` and `HouseCleaningService` JSON-LD with phone, email, area served and services
- Open Graph tags, canonical URL, sitemap and robots.txt
- Fonts (Inter and Poppins, Latin subset) are self-hosted in `assets/fonts/` and the hero fonts are preloaded, so no third-party requests block rendering
- Semantic headings (single H1), descriptive image alt text, lazy-loaded below the fold images, WebP images
- 1200x630 social sharing image (`assets/img/og-image.jpg`). During the preview, the `og:image` and `twitter:image` tags point at the GitHub Pages copy so link previews work; switch them back to `https://www.allcleanz.co.uk/assets/img/og-image.jpg` at launch
- `llms.txt` summary for AI assistants and search tools
- `robots.txt` and `sitemap.xml` (with image entries) point at the final domain, www.allcleanz.co.uk

## Launch settings (`netlify.toml`)

Ignored by GitHub Pages, active once the site is on Netlify:

- 301 redirects from all 21 old Wix URLs (e.g. `/end-of-tenancy-1`) to the matching new page or homepage section, so Google rankings carry over. When another service gets its own page, update its redirect
- Redirect from `allcleanz.co.uk` to `www.allcleanz.co.uk`
- Long browser caching for CSS, JS and fonts (bump the `?v=` value on every page when `styles.css` or `main.js` changes), 30 days for images
- Standard security headers

## Lead tracking

`main.js` sends events for phone clicks (`click_call`), WhatsApp clicks (`click_whatsapp`), email clicks (`click_email`) and quote form submissions (`quote_form_submit`), with where on the page the click happened. Nothing is sent until Google Analytics 4 (`gtag`) or Plausible is added to the pages; it then picks them up automatically. GA4 needs a cookie consent banner in the UK; Plausible does not.

## Hosting

Preview site (GitHub Pages, built from `main`): https://lukebrennan.github.io/AllCleanz/

The production host (Netlify, `allcleanz.netlify.app`) is paused until launch.

## Forms

The quote form (in the contact section) is a demo: it walks through service, property, frequency and contact details, then shows a summary. It does not send anything to an inbox yet, so connect it (for example with Netlify Forms) before launch. The confirmation screen's "Send these details on WhatsApp" button does work, as do the pre-filled WhatsApp links across the site.

## Preview passcode

While the site is in preview, every page shows a branded passcode screen (`assets/js/gate.js`, plus a one-line script at the top of each page's `<head>`). The passcode is not case sensitive. Once entered, the browser remembers it.

This is a deterrent, not real security: the page content is still delivered to the browser and the repository is public. Remove the gate before launch.

## Run locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000. The service pages are linked without `.html`, which GitHub Pages and Netlify handle; with this simple server, add `.html` to the address.
