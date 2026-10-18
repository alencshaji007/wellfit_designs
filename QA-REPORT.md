# Quality-check report

**Scope**: every page (`index.html`, `pages/about.html`, `services.html`, `projects.html`, `process.html`, `contact.html`, `404.html`).

**How it was tested**: the site was served by a plain static server (`python3 -m http.server`) and driven in headless Chromium through Playwright.
Testing ran in four parts:

1. Automated browser QA.
2. Interaction and regression suites.
3. A link and asset audit.
4. Two multi-agent adversarial code reviews, whose confirmed findings were fixed and re-tested.

No backend is required: the site is plain files and makes no third-party requests.

## 1. Source inspection

| Source | Checked | Result |
| --- | --- | --- |
| HTML reference (bundled design file) | Unpacked the bundle; extracted colours, fonts (embedded WOFF2), type scale, spacing, radii, buttons, inputs and the arch shape | Tokens implemented in `css/style.css`. Two accessibility-driven shades were added: `--rust-text` for small text, `--stone-strong` for form borders. |
| Final Website Content (DOCX) | Converted to Markdown; every page's copy taken from it | All six DOCX pages implemented. Bracketed "needs input" notes are not published (see README › Missing information). |
| Company profile (PDF, 17 pages) | Text extracted; all 61 embedded images reviewed | Supplementary facts only where consistent with the DOCX. Six genuine site photos used; stock or third-party images rejected. |
| Logo (JPG) | Byte-identical archive copy; derived transparent versions | Proportions unchanged (1.571:1); see ASSET-MANIFEST |

## 2. Automated browser QA (7 pages × 6 profiles = 42 runs)

The six profiles:

- desktop 1440×900
- laptop 1280×720
- tablet 820×1180 (touch)
- mobile 390×844 (touch)
- desktop with `prefers-reduced-motion: reduce`
- mobile with `prefers-reduced-motion: reduce`

On each run the page is scrolled top to bottom, then checked as follows:

| Check | Result |
| --- | --- |
| Console errors or warnings, uncaught exceptions | **0** in all 42 runs |
| Failed or 4xx/5xx requests | **0** |
| Horizontal overflow | **none** at any width |
| Images failing to decode | **0** |
| Reveal animations that never triggered | **0** |
| Images without `alt` | **0** (decorative textures use `alt=""` + `aria-hidden`) |
| Exactly one `<h1>` per page | **yes** |
| Duplicate `id`s | **none** |
| Interactive targets smaller than 40 px (excluding inline text links) | **none** |

## 3. Interaction suite (46/46 passed) and regression suite (23/23 passed)

**Navigation and menu**

- Mobile menu: opens and moves focus to its own visible **Close** button. It traps Tab; Close, Escape and links all close it, with focus returning to the menu toggle. The background is `inert` while it is open.
- Phone layout: on the home page and every inner page, the hero image comes before the headline, and the headline still starts within the first screen (390 × 844).
- Page transitions: the curtain covers on leave and clears on arrival; modifier-clicks and new tabs are untouched; bfcache restore is clean.
- Header turns solid on scroll, hides on scroll-down, and reappears on scroll-up or keyboard focus.
- In-page anchors land below the fixed header. They update the hash without stacking duplicate history entries, and move focus to the target.
- Cross-page anchor (`contact.html#enquiry`) lands on the form.

**Motion and scrolling**

- Smooth scrolling is on for mouse and trackpad only, and eases (intermediate positions observed).
- It hands over immediately to scrollbar drags, keyboard scrolling and scripted scrolls.
- Desktop hero pins and the arch opens. The "Illustrative render" badge stays inside the arch.
- The horizontal project rail moves with vertical scroll; keyboard focus on a card scrolls it into view.
- Marquee pause button stops the movement (`aria-pressed`).
- Reduced motion: no pinning, no smoothing, no transitions; every reveal is visible immediately.
- No JavaScript: all content visible. A watchdog also restores a static page if the scripts fail to start.

**Page features**

- Projects: the filters show the correct counts (7 / 5 / 2) and announce them in a live region.
- Lightbox: opens and shows the genuine photos, arrow keys page through them, Escape closes, and focus returns to the opener. A quick reopen works, and touch swipe is enabled.
- FAQ: accordion opens and closes, including when interrupted mid-animation.
- Enquiry form:
  - Empty submit flags every required field and focuses the first one. Email and phone formats are validated with clear messages.
  - A valid submit opens the email app with a pre-filled message, and the status text never claims the enquiry was sent.
  - Very long descriptions are shortened in the email link, with a notice.

## 4. Links, anchors and assets

`774` internal references checked (`href`, `src`, `srcset`, `imagesrcset`, gallery JSON):

- **0 missing files**
- **0 broken anchors**

The only external URLs are the site's own canonical domain.
Files present but not referenced by a page are intentional: the share image, the manifest icons, the master transparent logo used by structured data, and the archive copy of the original logo.

## 5. Performance (Chromium, local static server, no network throttling)

| Profile | Page | FCP ms | LCP ms | CLS | Long-task ms (>50 ms) | Transfer KB (initial load) | Requests |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| desktop | index.html | 84 | 84 | 0 | 0 | 316 | 12 |
| desktop | pages/about.html | 72 | 72 | 0 | 0 | 277 | 12 |
| desktop | pages/services.html | 92 | 92 | 0 | 0 | 277 | 12 |
| desktop | pages/projects.html | 72 | 72 | 0 | 0 | 327 | 18 |
| desktop | pages/process.html | 72 | 72 | 0 | 0 | 268 | 12 |
| desktop | pages/contact.html | 72 | 72 | 0 | 0 | 302 | 14 |
| mobile (4× CPU slowdown) | index.html | 240 | 240 | 0 | 50 | 293 | 12 |
| mobile (4× CPU slowdown) | pages/about.html | 188 | 188 | 0 | 20 | 264 | 12 |
| mobile (4× CPU slowdown) | pages/services.html | 248 | 248 | 0 | 63 | 269 | 12 |
| mobile (4× CPU slowdown) | pages/projects.html | 212 | 212 | 0 | 24 | 321 | 16 |
| mobile (4× CPU slowdown) | pages/process.html | 180 | 180 | 0 | 12 | 262 | 12 |
| mobile (4× CPU slowdown) | pages/contact.html | 184 | 184 | 0 | 21 | 264 | 14 |

Measures that keep these numbers low:

- **Images**: AVIF with WebP fallback, served at five widths. Explicit `width`/`height` and lazy loading below the fold. The hero is preloaded and has `fetchpriority="high"`.
- **Fonts**: two self-hosted WOFF2 files, preloaded, with `font-display: swap`.
- **Scripts**: about 51 KB of unminified JavaScript (about 13 KB gzipped), all deferred. One `requestAnimationFrame` loop drives every scroll effect; layout is measured on resize, not each frame.
- **Layout stability**:
  - The pinned hero is applied before first paint, so CLS is 0.
  - Reveal states start at 0.1 % opacity rather than 0, so above-the-fold text counts for LCP without changing the look.

Real-world numbers depend on hosting, CDN and connection. Enable compression and long cache lifetimes for `assets/`, `css/` and `js/`.

## 6. Accessibility

- **Structure**: semantic landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page with ordered headings, and a skip link.
- **Visible focus**: on all controls, including the gallery buttons (inset ring) and the marquee pause button.
- **Buttons**: every button on every page was measured at phone width, both normal and in the tapped/hover state, including the one in the mobile menu. All 18 are at least 6.9:1. Button text sits on its own layer above the hover fill.
- **Contrast** (WCAG 2.x ratios on the actual backgrounds):

  | Pair | Ratio |
  | --- | ---: |
  | Body ink on sand | 14.3:1 |
  | Secondary text on sand | 8.5:1 |
  | Eyebrows and small accent text (`#A9421A`) on sand | 4.8:1 |
  | White on navy buttons | 8.6:1 |
  | Navy ghost buttons | 6.9:1 |
  | Apricot on ink | 8.7:1 |
  | Large accent headings (`#B8481A`) | 4.2:1 (≥ 3:1 for large text) |
  | Form-control borders | 3.7:1 (WCAG 1.4.11) |

- **Motion**: honours `prefers-reduced-motion`, including when it is switched on after load. Moving content can be paused (marquee), and the hover preview can be dismissed with Escape.
- **Modal UI**: the mobile menu is a modal dialog with a focus trap, Escape to close and an inert background. The lightbox uses the dialog role with a focus trap and returns focus.
- **Forms**: visible labels, `aria-describedby` errors, `aria-invalid`, an error summary, autocomplete hints, and a honeypot field hidden from assistive technology.

## 7. Adversarial reviews

Two multi-agent review workflows covered:

- content fidelity
- accessibility
- JavaScript robustness
- CSS and responsiveness
- SEO and hosting
- brand and brief compliance
- a re-check of the fixes

Each finding was meant to be challenged by verifiers instructed to refute it.

**First review.** The verification step hit a usage limit, so its 29 findings were triaged by hand against the code. Every reproducible one was fixed in commit `b909172`, then re-tested by the regression suite. Fixes:

- mobile-menu stacking and dialog semantics
- unreadable menu CTA
- eyebrow contrast on dark cards
- caption and placeholder-note legibility
- form border contrast
- marquee pause control
- hover-preview dismissal
- gallery focus ring
- hero badge placement
- focus on faded or unrevealed content
- anchor offset under reveal transforms
- duplicate history entries
- programmatic scroll cancelled by non-scroll keys
- lightbox quick reopen and touch swipe
- FAQ interruption
- mailto length
- runtime reduced-motion changes
- older-Safari `MediaQueryList` fallback
- missing "Illustrative render" labels (intro inset, hover previews, share image)
- an "Our Story" heading that over-reached the DOCX wording

**Second review.** See the results appended below.

## 8. Known limitations

- **Content**: items needing client input are listed in README › *Missing information*. They cover client-name verification, photo approvals, testimonials, project timelines and the address.
- **Enquiry form**: it uses the visitor's email app until a form endpoint is configured (`data-endpoint`).
- **Illustrative renders**: these are clean, stylised CG and are clearly labelled. Professional photography of completed Wellfit projects should replace them over time.
- **Test coverage**: Chromium only; the code avoids engine-specific APIs, or guards them. Run a final pass on real Safari (iOS and macOS) and Firefox before launch, especially for the pinned hero and smooth-scroll feel on trackpads.
