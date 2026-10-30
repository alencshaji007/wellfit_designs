# Wellfit Designs — website

A static marketing website for **Wellfit Designs**, the operational brand of
WELL FIT SPACE DECORATION DESIGN & IMPLEMENTATION L.L.C. (Dubai, UAE). It is built with
plain HTML, CSS and vanilla JavaScript. There are no frameworks, no build step, no backend and no third-party
runtime dependencies.

- **Design tokens**: taken from the supplied HTML reference: colours, DM Serif Display + Jost, type scale, spacing, radii and the arch motif.
- **Content**: taken from *Wellfit Designs – Final Website Content.docx*. The *company profile PDF* was used only where it supported the DOCX.
- **Logo**: the client-supplied file, used unchanged in identity and proportions. Only its white background was removed for the transparent variant.
- **Motion**: smooth inertial scrolling, an arch window that opens to full-bleed on scroll, masked text and image reveals, parallax, a pinned horizontal project rail, a scroll-reactive marquee and page-to-page curtain transitions. All of it is disabled for visitors who prefer reduced motion.

---

**Dependencies**: there are no CDN or third-party requests. Fonts, scripts and images are all served from this folder.
The 3D (Three.js) layer from the original brief was dropped at the client's request in favour of scroll-driven motion,
so there is no `3d-scene.js` and no `assets/models/`.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home: hero, introduction, quick facts, services, who we serve, why Wellfit, featured projects, process, materials and craftsmanship, call to action |
| `pages/about.html` | About Us: who we are, story timeline (2020 → 2025), mission, vision, values, operating strength |
| `pages/services.html` | Our Services: eight services with scope lists and an on-page service navigator |
| `pages/projects.html` | Projects: filterable portfolio and a photo lightbox for projects that have genuine photographs |
| `pages/process.html` | Our Process: six steps and an FAQ |
| `pages/contact.html` | Contact Us: contact details, call / email quick actions, social links and the brochure download |
| `404.html` | Not-found page; uses root-absolute paths (see Deployment) |

## Folder structure

```
index.html, 404.html, robots.txt, sitemap.xml, site.webmanifest
pages/                 about, services, projects, process, contact
css/style.css          tokens, base, components, page sections
css/animations.css     reveal states, keyframes, reduced-motion overrides
css/responsive.css     breakpoints 1280 / 1100 / 1024 / 820 / 600 / 380
js/animations.js       motion engine: smooth scroll, scroll loop, reveals, parallax, hero, rail, marquee
js/navigation.js       header states, accessible mobile menu, anchors, page curtain transitions
js/main.js             boot, back-to-top, FAQ, project filters, lightbox, social-link placeholders (WhatsApp)
assets/fonts/          self-hosted WOFF2 fonts + OFL.txt
assets/logo/           original logo, transparent logo, mark, favicons
assets/brochure/       company profile PDF (downloadable)
assets/images/         home/, about/, services/, process/, projects/ (client images); hero/, details/, materials/ (renders)  (AVIF + WebP, responsive widths)
tools/renders/         Blender scripts that produced the illustrative renders (see ASSET-MANIFEST.md)
```

## Run locally

Any static file server works. From the project folder:

```bash
python3 -m http.server 8080
# then open http://localhost:8080/
```

or `npx http-server -p 8080`. Opening `index.html` straight from disk (`file://`) also works.
The 404 page and the web manifest expect to be served from a web root.

### GitHub Codespaces

On GitHub, open **Code → Codespaces → Create codespace on this branch**. The `.devcontainer/devcontainer.json` config
starts `python3 -m http.server 8080` automatically and opens the site in a new tab. If the tab does not open, use the
**Ports** panel and click the globe icon next to port 8080 ("Website").

To start the server by hand (for example after stopping it), run this in the codespace terminal:

```bash
python3 -m http.server 8080
```

Changes to HTML, CSS or JS show up after a browser refresh; no restart is needed.

## Deployment

Upload the folder as-is to any static host: Netlify, Vercel (static), Cloudflare Pages, GitHub Pages, S3 + CloudFront or shared hosting.
No build command is needed and the publish directory is the project root.

- **Custom domain at the root** (`https://www.wellfitdesigns.com/`): everything works as shipped, including `404.html`.
- **Hosts with "pretty URLs"**: Cloudflare Pages always does this, as does Vercel with `cleanUrls`. These hosts redirect `/pages/about.html` to `/pages/about`.
  - The site still works, because links are followed through the redirect.
  - For clean SEO, either turn the feature off where the host allows it, or change the canonical URLs, `og:url` values and `sitemap.xml` entries to the extensionless form.
  - Netlify, GitHub Pages, S3 and shared hosting serve the `.html` URLs directly.
- **Hosting in a sub-folder** (for example a GitHub Pages project URL `/<repo>/`): all pages work, but edit the
  root-absolute links in `404.html` and the icon paths in `site.webmanifest`.
- Canonical URLs, Open Graph URLs, `robots.txt` and `sitemap.xml` assume `https://www.wellfitdesigns.com`.
  Update them if the live domain or protocol differs.
- Recommended host headers: long cache lifetimes for `/assets/*`, `/css/*` and `/js/*`, plus compression (gzip or brotli) for HTML, CSS and JS.

## Editing content

Pages are plain HTML. The header, mobile menu and footer are repeated in every page.
When you change navigation, contact details or the footer, update all seven HTML files.
Text in the pages comes from the DOCX; keep any new copy factual.

**Images** use `<picture>` with AVIF and WebP sources at several widths. To add or replace an image:

1. Export a high-quality master (JPEG, PNG or WebP).
2. Run `python3 tools/renders/optimize.py master.jpg assets/images/<folder> <descriptive-name>`. This needs Pillow 11 or newer, built with AVIF support.
3. Reference the generated widths in the page's `srcset`. Keep `width` and `height` set to the master size, and write a meaningful `alt`.

**Replacing an illustrative render with a real photograph**: swap the files, update the `alt`, and remove the
`<span class="media-caption">Illustrative render</span>` label next to it.

**Adding a project** (`pages/projects.html`, plus the featured rail in `index.html`):

1. Copy an existing card and swap in the new photographs, name, location, category and description.
2. Update the gallery button markup. Its `data-gallery` JSON lists each photo's AVIF and WebP `srcset`, `alt`, `w`, `h` and `caption`.

## Motion system

All motion lives in `js/animations.js` and `css/animations.css`:

| Attribute / class | Effect |
| --- | --- |
| `data-reveal` (`fade`, `left`, `scale`, `mask`, `mask-side`, `line`) | Reveals the element when it enters the viewport |
| `data-split` | Words of a heading rise from a mask, staggered |
| `data-stagger="0.08"` | Staggers the reveals of children |
| `data-parallax="0.1"` | Element (or the image inside a `.media` frame) drifts against the scroll |
| `data-fill` | Statement words light up as you scroll |
| `data-progress="--var"` + `data-progress-step` | Drives a CSS variable (process line, timeline) and activates steps |
| `data-hero`, `data-rail`, `data-marquee` | Hero arch opening, pinned horizontal rail, velocity-aware marquee |
| `data-magnetic` | Subtle magnetic pull on buttons (fine pointers only) |

How motion adapts to the device:

- **Smooth scrolling** is enabled only for mouse and trackpad users (`hover: hover` and `pointer: fine`). Touch devices keep native scrolling.
- **Pinned effects** (hero, rail) need a viewport at least 1025 px wide and 560 px tall. Smaller screens get a stacked layout.
- **`prefers-reduced-motion: reduce`** turns off smooth scrolling, pinning, parallax, reveals, the marquee and page transitions. All content is shown immediately.
- **Without JavaScript**, every element is visible; reveal states are scoped to `html.js`. A watchdog removes `js` if the scripts fail to start.

## Contact page

The contact page has no form. Visitors call (`tel:` link) or email; the email button opens the visitor's email app with a
short template (project type, location, area, description, preferred contact method) addressed to `projects@wellfitdesigns.com`.
The "Request a Quote" buttons across the site point to `pages/contact.html#enquiry`, the contact section.

## Social media links

The footer of every page and the contact page show WhatsApp, Instagram, Facebook, LinkedIn and YouTube icons. The profile
links open in a new tab:

| Network | URL |
| --- | --- |
| Instagram | `https://www.instagram.com/wellfit_designs_/` |
| Facebook | `https://www.facebook.com/share/1LdYV6WJf3/` |
| LinkedIn | `https://www.linkedin.com/company/wellfitdesigns/` |
| YouTube | `https://www.youtube.com/@Wellfitdesigns` |

WhatsApp has no URL yet, so it stays `href="#"`; `js/main.js` marks such links as disabled (`aria-disabled="true"`) and
stops them jumping to the top of the page. To change a profile, search the HTML files for `data-social="instagram"`
(or `whatsapp`, `facebook`, `linkedin`, `youtube`) and replace the `href`. Each icon appears twice on `pages/contact.html` and
once on every other page (`index.html`, `404.html` and the files in `pages/`). For WhatsApp use `https://wa.me/971XXXXXXXXX`
(country code and number, no `+` or spaces) and add `target="_blank" rel="noopener noreferrer"` like the other profiles.

## Company profile brochure

`assets/brochure/wellfit-designs-company-profile.pdf` is offered for download on the home page (a "Company Profile" section
before the closing call to action), in the footer Quick Links on every page, and on the contact page. Links use the `download`
attribute, so the file is saved as `Wellfit-Designs-Company-Profile.pdf`; "View online" opens it in a new tab.
To update the brochure, replace the PDF with the same file name, and update the "PDF · 2.3 MB · 17 pages" line in `index.html`
and the cover image (`assets/images/home/brochure-cover-*`, rendered from page 1).

## Missing information and items to confirm before launch

Nothing below was invented on the site. Each item is either left out or flagged.

1. **Residential project names.** "Richard Sanchez" (DAMAC Hills) appears in the DOCX and the PDF. However, the name, like the PDF testimonial names, matches placeholder names that design templates commonly use. Please confirm it is a real client and that you have permission to publish it, or rename or remove the card. (The former "Avery Davis Home" card has been replaced by Eleonora Apartment.)
2. **Testimonials.** The PDF contains three testimonials (Helene Paquet, Jamie Chastain, Sebastian Bennett) with stock-style portraits, and the final DOCX does not include them. No testimonials are published. Supply genuine, approved testimonials to add a section.
3. **PDF imagery.** The PDF's cover, "who we are" and expertise images appear to be third-party or stock images (one carries an "EXS OFFICES" watermark), so none of them are used. All project images now come from the client's October 2026 image supply.
4. **Client-supplied images.** Please confirm the rights to every supplied image and check the DOCX project descriptions against the completed scope. The project images are computer-generated and are labelled "Visualisation" (on-image label, `alt` text, lightbox caption and footer note); remove the label from any image replaced by a real photograph.
5. **Eleonora Apartment and Fatima Majlis locations.** Not supplied, so the cards show "UAE". The Fatima Majlis description was written from its two images; please confirm it. (Client name confirmed: "Smart Leaves".)
6. **Project timelines.** The FAQ answer for project duration has no typical ranges; the DOCX placeholder asks for them.
7. **Not provided, so not shown.** Street address or map, opening hours, trade licence number, WhatsApp number, team members, awards and certifications.
8. **Claims softened per the DOCX.** The PDF also says "established in 2020", "5 years experience", "state-of-the-art production facility" and lists "Architecture" expertise. The DOCX deliberately words these differently: the journey began in 2020 with JAN Interior Fit Out, and Wellfit Designs was established in 2025. The DOCX wording is used throughout.
9. **Social media links.** Instagram, Facebook, LinkedIn and YouTube are live; the WhatsApp icon is a placeholder until a WhatsApp number is confirmed. See *Social media links* above.
10. **Analytics and cookie consent.** Not included. Add them if required, and update the privacy wording accordingly.
11. **Illustrative renders.** The Home, About, Services, Process and Projects images are client-supplied. The Contact image and the material swatches are still original renders labelled "Illustrative render"; replace them when client images are available.

## Browser support

Current Chrome, Edge, Safari 15.4+ and Firefox. This covers AVIF/WebP via `<picture>`, CSS container query units with px fallbacks, `clip-path`,
individual transform properties, `IntersectionObserver` and `ResizeObserver`. Older browsers fall back to static layouts.

See **ASSET-MANIFEST.md** for every asset and its provenance, and **QA-REPORT.md** for the test results.
