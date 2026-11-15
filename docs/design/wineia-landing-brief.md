# WineAI landing — design brief (FLV-inspired)

**Status:** draft for product/design  
**Inspiration source:** [Fondation Louis Vuitton](https://www.fondationlouisvuitton.fr/en) (structure, type pairing, whitespace — **not** brand, logo, imagery, or Typekit licenses)  
**Date:** 2026-11-14 (America/Sao_Paulo)

This brief defines how a WineAI marketing / waitlist landing should feel. It is **not** a clone of FLV. WineAI stays a WhatsApp sommelier product; the reference only supplies editorial luxury patterns (hero plane, dual type, quiet chrome).

---

## 1. Brand test (first viewport)

After removing the nav, the first screen must still read as **WineAI** — not a museum, not a wine shop aggregator.

| Must appear in the first viewport | Must not appear there |
|-----------------------------------|------------------------|
| Brand name **WineAI** at hero scale | Stats, schedules, plan comparison tables |
| One headline | Feature icon rows, pill clusters |
| One short supporting sentence | Cards in the hero |
| One CTA group (primary + optional secondary) | Floating badges / promo stickers on the image |
| One dominant full-bleed image (atmosphere: cellar, glass, vineyard light — licensed or owned) | Inset hero card / side-panel collage |

**Composition:** one plane. Edge-to-edge image or tonal field behind type. No dashboard chrome.

---

## 2. Visual direction (WineAI, not FLV)

| Axis | Direction |
|------|-----------|
| Mood | Quiet luxury, editorial, night-glass, sober |
| Base | Near-white warm-neutral paper **or** deep ink — pick **one** per page; default **light paper** for launch |
| Accent | Deep **garnet** (`#6B1E2E`) — wine signal without terracotta/cream cliché |
| Secondary | Soft stone gray for rules and meta |
| Avoid | Purple/indigo AI gradients; cream + terracotta; newspaper broadsheet; glow; emoji; multi-layer shadows; rounded-full pill farms |

FLV uses garden/azur/electric accents for a cultural institution. WineAI replaces those with **garnet + stone** so the product does not look like a Fondation site with the logo swapped.

---

## 3. Typography

FLV pairs **Futura PT** (display/UI) + **Adobe Garamond Pro** (body). Those faces are licensed via Adobe Fonts — **do not embed Typekit kit `lku3gps` or FLV font files**.

| Role | WineAI choice (Google Fonts / open) | Notes |
|------|-------------------------------------|--------|
| Display / nav / labels | **Syne** (600–700) or **Outfit** (500–600) | Geometric sans; uppercase labels with `letter-spacing: 0.04em` |
| Body / long read | **Cormorant Garamond** or **Source Serif 4** | Editorial serif; 18–20px body, generous line-height |
| Mono (rare) | System mono only for codes | Do not decorate the landing with code |

### Type scale (CSS classes)

```css
.f-display {
  font-family: "Syne", sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.01em;
  line-height: 0.95;
  font-size: clamp(2.75rem, 9vw, 6.5rem);
}

.f-title {
  font-family: "Syne", sans-serif;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  line-height: 1.15;
}

.f-label {
  font-family: "Syne", sans-serif;
  font-weight: 600;
  font-size: 0.8125rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.f-body {
  font-family: "Cormorant Garamond", "Source Serif 4", Georgia, serif;
  font-size: clamp(1.125rem, 1.2vw, 1.25rem);
  line-height: 1.45;
  font-kerning: normal;
}

.f-caption {
  font-family: "Cormorant Garamond", Georgia, serif;
  font-size: 1rem;
  line-height: 1.35;
  color: var(--color-stone-60);
}
```

---

## 4. Color tokens

```css
:root {
  /* Paper */
  --color-paper: #f7f6f3;
  --color-paper-elevated: #ffffff;
  --color-ink: #1a1a1a;
  --color-ink-muted: #5a5c5c;

  /* Stone (FLV-like gray ladder, renamed) */
  --color-stone-05: #f6f6f5;
  --color-stone-10: #e9e9e7;
  --color-stone-20: #ddddda;
  --color-stone-40: #b0b3af;
  --color-stone-60: #747676;
  --color-stone-80: #303030;

  /* Wine accent (WineAI — not FLV garden/azur) */
  --color-garnet-40: #8b2e40;
  --color-garnet-50: #6b1e2e;
  --color-garnet-70: #3f121c;

  --color-text: var(--color-ink);
  --color-bg: var(--color-paper);
  --color-accent: var(--color-garnet-50);
  --color-accent-contrast: #ffffff;
}
```

Dark section (optional mid-page band): `--color-bg: var(--color-ink)` and reverse type; keep the **first** viewport on paper or full-bleed photo with light type — one choice only.

---

## 5. Spacing & motion

Inspired by FLV’s spacing ladder; keep the same rhythm, not their class names.

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 80px;
  --space-10: 120px;

  --ease-link: 0.2s ease;
  --ease-panel: 0.35s ease;
}
```

**Motion (2–3 intentional):**

1. Hero brand/headline fade-up once on load (~400ms).  
2. Primary CTA underline or color settle on hover (`--ease-link`).  
3. Optional slow ken-burns (≤3%) on the hero image only — no scroll-jacking.

---

## 6. Page structure (one job per section)

| # | Section | Purpose | Content budget |
|---|---------|---------|----------------|
| 0 | **Hero** | Brand + promise + CTA | WineAI, 1 headline, 1 sentence, CTA group, full-bleed visual |
| 1 | **How it works** | One idea: WhatsApp pocket sommelier | 1 headline + 1 short paragraph + optional single still (phone frame optional, not a card grid of 6) |
| 2 | **Tiers** | ENTRY vs SUPERIOR at a glance | Two columns of text, not product cards with shadows; link to commercial doc later |
| 3 | **Cadence** | Trust: scheduled recommendations, education opt-in | One sentence each; no calendar widgets |
| 4 | **Footer** | Legal / contact / LGPD placeholder | Quiet links; Portuguese when shipping BR |

**Default: no cards.** If a control needs a hit target (tier picker), a borderless column is enough. Removing radius/shadow/background must not break comprehension.

---

## 7. Components (minimal)

| Component | Spec |
|-----------|------|
| **Primary CTA** | Solid garnet, white label (`.f-label`), rectangular or 2px radius max — not pill |
| **Secondary CTA** | Text + bottom border / underline; ink on paper |
| **Nav** | Brand left (wordmark text), 3–4 links right; transparent over hero until scroll |
| **Divider** | 1px `stone-20`, full bleed or content width — no heavy rules |
| **Form (waitlist)** | Single email or phone field + submit; labels in `.f-label`; errors in caption serif |

---

## 8. Content direction (PT-BR draft)

| Slot | Copy (draft) |
|------|----------------|
| Brand | WineAI |
| Headline | Seu sommelier no bolso |
| Support | Recomendações de vinho no WhatsApp — com calma, critério e o seu ritmo. |
| Primary CTA | Entrar na lista |
| Secondary CTA | Como funciona |

Tone: Portuguese, intimate, not salesy. Avoid “AI-powered” jargon in the hero.

---

## 9. Legal / IP guardrails

- Do **not** reuse FLV logo, photography, CSS bundle `app.*.css`, or Adobe Fonts kit.  
- Do **not** mirror distinctive building imagery of the Fondation.  
- Inspiration is limited to: dual type pairing, whitespace, uppercase labels, full-bleed hero, quiet footer.  
- Commission or license wine/atmosphere photography for the hero.

---

## 10. Implementation notes

**Prototype (static):** [`frontend/landing/`](../../frontend/landing/) — `index.html` + `styles.css` + `assets/hero.jpg` (Unsplash atmosphere photo; replace with owned/licensed art before launch).

- CSS variables from §4–5 live in `styles.css` `:root`.
- Fonts: Google Fonts **Syne** + **Cormorant Garamond**.
- Local preview: from `frontend/landing`, `python3 -m http.server 8765 --bind 127.0.0.1`.
- Backend remains WhatsApp/Cloud Run; this landing is a **separate front** until product decides hosting (Cloud Storage + CDN, etc.).
- Waitlist form is visual only (no backend hookup yet).

---

## 11. Acceptance checklist (design judge)

- [ ] First viewport fails the “another brand” test without the word WineAI.  
- [ ] No cards in the hero; ≤1 primary CTA.  
- [ ] Fonts are Syne (or Outfit) + Cormorant/Source Serif — not Inter/Roboto/Arial as primary.  
- [ ] Accent is garnet, not purple gradient or terracotta-on-cream.  
- [ ] No FLV assets or Typekit kit IDs in the repo.  
- [ ] Sections each have one job and one headline.

---

## Related

- Product: [docs/commercial.md](../commercial.md), [docs/COMMERCIAL-LAUNCH.md](../COMMERCIAL-LAUNCH.md)  
- Architecture context: [docs/decision.md](../decision.md)  
- Inspiration URL (reference only): https://www.fondationlouisvuitton.fr/en
