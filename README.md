# All Cleanz Website

New landing page for [All Cleanz](https://www.allcleanz.co.uk/), a domestic and commercial cleaning company based in Prescot, Merseyside.

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

Photos: service cards use the photos from the current site. Two stock photos come from Unsplash (free for commercial use under the Unsplash License):

- Hero, `assets/img/hero-upholstery-cleaning*.webp`: Giorgio Trovato, https://unsplash.com/photos/5TXz228u4eo
- About, `assets/img/about-cleaning.webp`: Vitaly Gariev, https://unsplash.com/photos/ViXT4S89hS0

## SEO

- Title and meta description targeting "cleaning company Prescot / Merseyside"
- `WebSite` and `HouseCleaningService` JSON-LD with phone, email, area served and services
- Open Graph tags, canonical URL, sitemap and robots.txt
- Semantic headings (single H1), descriptive image alt text, lazy-loaded below the fold images, WebP images
- 1200x630 social sharing image (`assets/img/og-image.jpg`)
- `llms.txt` summary for AI assistants and search tools
- `robots.txt` and `sitemap.xml` (with image entries) point at the final domain, www.allcleanz.co.uk

## Hosting

Preview site (GitHub Pages, built from `main`): https://lukebrennan.github.io/AllCleanz/

The production host (Netlify, `allcleanz.netlify.app`) is paused until launch.

## Run locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000.
