---
name: Cyber Midnight
colors:
  surface: '#0c1324'
  surface-dim: '#0c1324'
  surface-bright: '#33394c'
  surface-container-lowest: '#070d1f'
  surface-container-low: '#151b2d'
  surface-container: '#191f31'
  surface-container-high: '#23293c'
  surface-container-highest: '#2e3447'
  on-surface: '#dce1fb'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dce1fb'
  inverse-on-surface: '#2a3043'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#bec6e0'
  on-tertiary: '#283044'
  tertiary-container: '#9ba2bb'
  on-tertiary-container: '#31394d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#dae2fd'
  tertiary-fixed-dim: '#bec6e0'
  on-tertiary-fixed: '#131b2e'
  on-tertiary-fixed-variant: '#3f465c'
  background: '#0c1324'
  on-background: '#dce1fb'
  surface-variant: '#2e3447'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style
The design system adopts a "Cyber Midnight" aesthetic, a high-fidelity evolution of the Sentinel X framework. It is engineered for high-stakes technical environments where focus and clarity are paramount. The style merges **Minimalism** with subtle **Glassmorphism** to create a multi-layered interface that feels deep and immersive.

The brand personality is precise, authoritative, and advanced. It targets power users—developers, security analysts, and engineers—who require a UI that recedes into the background while highlighting critical data. The emotional response is one of calm control and technological sophistication, achieved through a dark-mode-first approach with high-energy accents.

## Colors
The palette is built on a foundation of "Midnight" neutrals. The base surface is a near-black slate, providing maximum contrast for the vibrant Emerald Green primary accent.

- **Primary (#10B981):** A sharp Emerald Green used for primary actions, success states, and critical paths. It represents "system active" and "secure."
- **Secondary (#6366F1):** A deep Indigo used for interactive components, focus states, and decorative data visualizations.
- **Surface Palette:** The background uses a deep Navy-Black (#020617). Containers and elevated surfaces use a layered Indigo-Slate (#0F172A) to create structural depth without losing the "dark" feel.
- **Accents:** Use a low-opacity Indigo for hover states and secondary buttons to maintain the monochromatic depth of the background.

## Typography
This design system utilizes **Inter** across all levels to ensure a systematic, utilitarian, and highly legible experience. 

- **Headlines:** Use tighter letter spacing and semi-bold weights to command attention against the dark background.
- **Body Text:** Standard weights are used with generous line heights to prevent "halo" effects or eye strain in low-light environments.
- **Labels:** Small-caps or increased tracking should be applied to metadata labels to distinguish them from actionable body text.

## Layout & Spacing
The system follows a strict **8px grid** (Round Eight) to maintain mathematical harmony and alignment. 

- **Desktop:** A 12-column fluid grid with 24px gutters. Margins are fixed at 64px to create a focused "cockpit" feel in the center of the screen.
- **Mobile:** A 4-column grid with 16px gutters and margins.
- **Spacing Logic:** Vertical rhythm is managed through increments of 8px. Use 16px (md) for internal component padding and 24px (lg) for spacing between distinct functional blocks.

## Elevation & Depth
In the "Cyber Midnight" environment, depth is communicated through **Tonal Layers** and **Backdrop Blurs** rather than traditional drop shadows.

- **Level 0 (Base):** The deepest layer (#020617). No borders.
- **Level 1 (Containers):** Indigo-Slate (#0F172A). Used for cards and main content areas.
- **Level 2 (Overlays):** A translucent version of Level 1 with a 12px backdrop blur and a 1px "ghost border" (Indigo at 20% opacity).
- **Interactions:** Hovered elements should glow slightly using a low-spread shadow tinted with the primary Emerald Green (#10B981) at 15% opacity.

## Shapes
The shape language is controlled and modern. We use a **Rounded** (0.5rem) baseline to soften the technical edge of the system, making it feel approachable while maintaining a professional silhouette.

- **Standard Elements:** 8px (0.5rem) radius for buttons and input fields.
- **Containers:** 16px (1rem) radius for large cards and modular sections.
- **Dynamic Elements:** Large 24px (1.5rem) radius for contextual floating menus or feature highlights.

## Components
- **Buttons:** Primary buttons are solid Emerald Green with black text for maximum contrast. Secondary buttons use an Indigo outline with semi-transparent fills.
- **Inputs:** Fields use the Level 1 surface color with a 1px Slate border. On focus, the border transitions to Emerald Green with a subtle outer glow.
- **Chips:** Small, high-contrast badges used for status. "Active" chips use Emerald Green text on a 10% opacity Green background.
- **Lists:** Rows are separated by thin 1px borders (#1E293B). Hovering over a list item should trigger a subtle shift to a lighter Indigo tint.
- **Cards:** Cards should have no shadow but must utilize the Level 1 surface color and the defined 16px (rounded-lg) corners to distinguish themselves from the background.
- **Status Indicators:** Use the Primary Emerald for success, but strictly reserve it for active system states to maintain the "Cyber Midnight" hierarchy.