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

All copy, services, claims and testimonials are taken from the existing allcleanz.co.uk site. Nothing has been invented. Photos are the ones already used on the current site.

## SEO

- Unique title and meta description targeting "domestic and commercial cleaning Prescot / Merseyside"
- `HouseCleaningService` JSON-LD with phone, email, area served, services and reviews
- Open Graph tags, canonical URL, sitemap and robots.txt
- Semantic headings (single H1), descriptive image alt text, lazy-loaded below the fold images, WebP images

## Run locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000.
