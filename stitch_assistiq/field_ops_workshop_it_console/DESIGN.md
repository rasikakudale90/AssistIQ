---
name: Field Ops & Workshop IT Console
colors:
  surface: '#fff8f2'
  surface-dim: '#e0d9d1'
  surface-bright: '#fff8f2'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#faf2ea'
  surface-container: '#f4ede5'
  surface-container-high: '#eee7df'
  surface-container-highest: '#e8e1d9'
  on-surface: '#1e1b17'
  on-surface-variant: '#46483d'
  inverse-surface: '#33302b'
  inverse-on-surface: '#f7f0e7'
  outline: '#77786c'
  outline-variant: '#c7c7b9'
  surface-tint: '#596337'
  primary: '#535c32'
  on-primary: '#ffffff'
  primary-container: '#6b7548'
  on-primary-container: '#f0fcc4'
  inverse-primary: '#c1cc97'
  secondary: '#a0401f'
  on-secondary: '#ffffff'
  secondary-container: '#fe8760'
  on-secondary-container: '#732101'
  tertiary: '#735300'
  on-tertiary: '#ffffff'
  tertiary-container: '#916a07'
  on-tertiary-container: '#fff4e8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde8b1'
  primary-fixed-dim: '#c1cc97'
  on-primary-fixed: '#171e00'
  on-primary-fixed-variant: '#414b22'
  secondary-fixed: '#ffdbd0'
  secondary-fixed-dim: '#ffb59d'
  on-secondary-fixed: '#390b00'
  on-secondary-fixed-variant: '#802a08'
  tertiary-fixed: '#ffdea4'
  tertiary-fixed-dim: '#f0bf5c'
  on-tertiary-fixed: '#261900'
  on-tertiary-fixed-variant: '#5d4200'
  background: '#fff8f2'
  on-background: '#1e1b17'
  surface-variant: '#e8e1d9'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-md:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: IBM Plex Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 22px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.08em
  label-sm:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
This design system captures the rugged utility, precision, and tactile clarity of a field-service technician's workshop manual. Built for high-volume diagnostics, equipment tracking, and IT ticket resolution, the interface avoids sterile enterprise SaaS tropes in favor of an authentic workshop clipboard and instrument-panel aesthetic.

### Brand Personality & Emotional Tone
- **Utilitarian & Honest:** No superfluous decorative fluff, no synthetic neon gradients, and zero glossy illusions. Every element signals purpose, durability, and operational directness.
- **Calm & Methodical:** The warm, muted stone and paper tones reduce eye strain during 10-hour technician shifts under industrial fluorescent lighting.
- **Instrument Precision:** Monospaced data readouts and structured index-card panels instill absolute confidence in timestamps, hardware MAC addresses, and SLA metrics.

### Design Movement
**Industrial Functionalism & Tactile Utility:** Blending Swiss information architecture with the physical tactility of heavy-stock job cards, embossed hardware tags, and stamped field-kit dockets. Hierarchy is driven by 1px hairline borders, muted pigment fills, and rigid spatial grids.

## Colors
The palette is grounded in natural, non-synthetic mineral pigments. It strictly bans hyper-saturated web primaries (no synthetic royal blues, cyan, or neon greens). Default mode is strictly light matte.

### Palette Roles
- **Canvas Base (`#E8E4DD`):** Warm stone gray representing unbleached workshop workbench surfaces.
- **Cards & Primary Surface (`#F2EFE9`):** Heavy warm bone paper matte. Used for elevated interactive panels, inspection dockets, and form containers.
- **Secondary Surface (`#DFDBD3`):** Recessed stone surface for sidebars, table headers, data wells, and inactive tab tracks.
- **Ink & Typography (`#2B2823`):** High-density charcoal ink. Used for all primary copy, borders, and icons to deliver crisp readability without harsh pure black.
- **Muted Muted Ink (`#6E6A62`):** Secondary metadata, helper notes, and hardware schematics.
- **Primary Accent (`#6B7548` - Burnt Olive):** Signifies active diagnostics, operational readiness, verified checklists, and confirmed actions.
- **Secondary Accent (`#B5502D` - Rust / Terracotta):** Reserved for SLA breach counters, hardware fault alerts, and destructive workshop commands.
- **Tertiary Accent (`#C89B3C` - Dusty Mustard):** Acknowledged items, triage queues, in-transit equipment, and pending vendor states.
- **Structural Border Ink (`#D1CCC0`):** Precise 1px borders delineating structural zones and form controls.

## Typography
Typography reflects technical documentation and calibration instruments. Three specialized families work in tandem:

- **Display & Headings (Space Grotesk):** Provides mechanical balance and authoritative presence for module titles, technician boards, and equipment categories.
- **Body & Editorial (IBM Plex Sans):** Engineered for technical clarity, resolving dense incident notes, hardware diagnostic logs, and instructions.
- **Telemetric & Code (JetBrains Mono):** Dedicated to serial codes, ticket tokens (`#TKT-8042`), IP addresses, uptime durations, and SLA countdowns.

### Formatting Directives
- **Micro-Labels:** Use `label-caps` strictly in all-caps with positive tracking (`0.08em`) for section heads, column headers, badge counters, and equipment specs.
- **Numeric Calibration:** All telemetry readouts and ticket IDs must use `JetBrains Mono` with tabular numbers (`tnum`) enabled to ensure vertical alignment across data lists.

## Layout & Spacing
The layout adheres to a rigid 8px spatial grid, reinforcing an engineered index-cabinet architecture.

### Grid & Structure
- **Desktop (12 Columns):** Fluid container with fixed 1px structural gutters. 24px outer margins. The workspace divides into a persistent 280px technician utility sidebar and a modular multi-column workspace.
- **Tablet (8 Columns):** Collapses auxiliary toolbars into drawer trays, prioritizing the primary ticket workbench. 16px outer margins.
- **Mobile (4 Columns):** Single-column stacked layout with full-width index cards, 12px outer margins, and sticky bottom utility actions for one-handed operation in the field.

### Density Rules
- High data density is prioritized over vast decorative whitespace.
- Margins between index-card modules are kept at `space-md` (16px) or `space-lg` (24px) to preserve visual connection between related telemetry panels.

## Elevation & Depth
This design system rejects deep drop shadows and synthetic floating blurs. Elevation is conveyed strictly through **tonal paper layering and architectural hairline framing**.

### Layering Hierarchy
1. **Workbench Bed (Lowest Layer):** `#E8E4DD` matte canvas.
2. **Sub-Panels & Recessed Trays (Mid-Low):** `#DFDBD3` with a 1px solid border (`#D1CCC0`).
3. **Index Cards & Ticket Sheets (Mid-High):** `#F2EFE9` with a 1px solid border (`#D1CCC0`). For slight separation, a flat 1px paper offset shadow (`0 1px 0 rgba(43, 40, 35, 0.08)`) is permitted.
4. **Modal Diagnostics & Flyouts (Top Tier):** `#F2EFE9` framed by a pronounced 1.5px outline in `#2B2823`, cast over an unblurred backdrop wash (`rgba(43, 40, 35, 0.4)`).

## Shapes
Geometry is disciplined, utilitarian, and boxy. Radii are confined to 2px to 4px to emulate precision-milled hardware casings, sheet-metal plates, and punched job cards.

- **Standard Elements (Buttons, Inputs, Cards):** 2px to 4px corner radius (`roundedness: 1`).
- **Pills and Capsules:** Strictly prohibited. Badges, tags, and chips are rectangular with sharp 2px corners or notched technical bevels.
- **Dividers:** 1px hairline lines using `#D1CCC0` or dashed `1px dashed #B8B3A8` for perforated job-ticket style divisions.

## Components

### Buttons & Actions
- **Primary (Burnt Olive):** Solid `#6B7548` background, `#F2EFE9` ink, 2px radius, uppercase monospaced text (`label-caps`). 1px solid `#575F3A` border. Hover drops brightness by 8%; active state triggers a 1px downward translation.
- **Urgent / Destructive (Rust):** Solid `#B5502D` background, `#F2EFE9` ink. Used strictly for critical overrides and SLA escalations.
- **Secondary / Utility:** `#DFDBD3` background, `#2B2823` ink, 1px solid `#D1CCC0` border. Hover turns to `#F2EFE9`.

### Status Chips & Priority Badges
- Compact rectangular dockets (`0.25rem 0.5rem` padding). 2px radius.
- Always include an uppercase monospaced code prefix (e.g., `[CRIT] SLA-01`, `[OPER] RUNNING`, `[HOLD] WAIT-PARTS`).
- **Critical / Breach:** `#B5502D` ink over `#F7E4DE` tinted surface with a 1px `#E0A996` border.
- **Active / Resolved:** `#6B7548` ink over `#EBF0E1` tinted surface with a 1px `#B8C49F` border.
- **Triage / Pending:** `#C89B3C` ink over `#FDF6E7` tinted surface with a 1px `#EAD098` border.

### Ticket & Diagnostic Cards
- Background: `#F2EFE9`. Border: 1px solid `#D1CCC0`.
- Split headers featuring a top perforated border (`1px dashed #D1CCC0`) displaying ticket ID in `JetBrains Mono` and relative timestamp on opposite poles.
- Hover state: Border shifts to `#2B2823` with no scale or elevation increase.

### Data Tables & Spec Lists
- Table headers set in `#DFDBD3`, borders in `#D1CCC0`, text in `label-caps` `#6E6A62`.
- Alternating row zebra-striping: `#F2EFE9` and `#ECE8E1`.
- Row height fixed at 40px for high information density.

### Form Inputs & Terminal Fields
- Background: `#FFFFFF` (warm-cast paper white) inset within `#DFDBD3` frames.
- Inactive state: 1px solid `#D1CCC0`. Focus state: 1.5px solid `#2B2823` with an immediate sharp highlight ring (`0 0 0 1px #2B2823`).
- Monospaced helper tags anchored within right-hand field boundaries.