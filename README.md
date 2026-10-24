# All Cleanz Website

New landing page for [All Cleanz](https://www.allcleanz.co.uk/), a domestic and commercial cleaning company based in Merseyside, working across the North West.

A static site: plain HTML, CSS and JavaScript with no build step.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Landing page: hero with call/WhatsApp CTAs, about, 14 services, Texatherm carpet cleaning, why choose us, clients, testimonials, contact |
| `under-construction.html` | Target for every other nav link. Reads `?page=<slug>` to show which page was requested. `noindex` |
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

Photos: service cards use the photos from the current site. Three stock photos come from Unsplash (free for commercial use under the Unsplash License):

- Hero, `assets/img/hero-home-cleaning*.webp`: PuroClean of Fort Worth, https://unsplash.com/photos/-dc38HdQR1M
- Before and after, `assets/img/before-after/`: All Cleanz's own photos from their Facebook page, aligned and cropped to match
- Recent work strip, `assets/img/recent/`: All Cleanz's own photos from their Facebook page; each tile links to the original post. Update by swapping the images and links in the RECENT WORK section of `index.html`
- Hero inset, `assets/img/cleaning-supplies.webp`: Giorgio Trovato, https://unsplash.com/photos/XxAy813D66I
- About, `assets/img/about-surface-cleaning.webp`: Towfiqu barbhuiya, https://unsplash.com/photos/ho-p7qLBewk

## SEO

- Title and meta description targeting "cleaning company Merseyside / North West"
- `WebSite` and `HouseCleaningService` JSON-LD with phone, email, area served and services
- Open Graph tags, canonical URL, sitemap and robots.txt
- Semantic headings (single H1), descriptive image alt text, lazy-loaded below the fold images, WebP images
- 1200x630 social sharing image (`assets/img/og-image.jpg`)
- `llms.txt` summary for AI assistants and search tools
- `robots.txt` and `sitemap.xml` (with image entries) point at the final domain, www.allcleanz.co.uk

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

Then open http://localhost:8000.
