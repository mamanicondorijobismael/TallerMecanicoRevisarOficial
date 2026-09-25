---
name: TAMGO Industrial Management
colors:
  surface: '#f9f9ff'
  surface-dim: '#d3daef'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#e9edff'
  surface-container-high: '#e1e8fd'
  surface-container-highest: '#dce2f7'
  on-surface: '#141b2b'
  on-surface-variant: '#44474e'
  inverse-surface: '#293040'
  inverse-on-surface: '#edf0ff'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#485f88'
  primary: '#001330'
  on-primary: '#ffffff'
  primary-container: '#0d284e'
  on-primary-container: '#7990bc'
  inverse-primary: '#b0c7f6'
  secondary: '#446082'
  on-secondary: '#ffffff'
  secondary-container: '#bad7fe'
  on-secondary-container: '#415d7f'
  tertiary: '#1c1200'
  on-tertiary: '#ffffff'
  tertiary-container: '#352600'
  on-tertiary-container: '#b58800'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e3ff'
  primary-fixed-dim: '#b0c7f6'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#30476e'
  secondary-fixed: '#d2e4ff'
  secondary-fixed-dim: '#acc9ef'
  on-secondary-fixed: '#001d36'
  on-secondary-fixed-variant: '#2c4869'
  tertiary-fixed: '#ffdf9d'
  tertiary-fixed-dim: '#f9bd14'
  on-tertiary-fixed: '#251a00'
  on-tertiary-fixed-variant: '#5b4300'
  background: '#f9f9ff'
  on-background: '#141b2b'
  surface-variant: '#dce2f7'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  display-md-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 28px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 24px
  gutter: 16px
  sidebar-width: 260px
---

## Brand & Style
The design system is engineered for high-stakes mechanical and tire service environments where precision, durability, and clarity are paramount. The aesthetic merges **Corporate Modern** efficiency with **Industrial Tech** utility. It evokes a sense of reliability and heavy-duty performance, mirroring the machinery it manages.

The interface prioritizes information density without sacrificing legibility. High-contrast navigation and structured data views ensure technicians and managers can operate the system in high-activity environments. The emotional response is one of organized control—transforming complex workshop logistics into a streamlined, high-tech workflow.

## Colors
The palette is anchored by "Deep Engine Blue" for structural elements, providing a grounded, authoritative feel. Gold is used surgically for high-priority highlights and "Pending" states, ensuring they catch the eye against the professional blue tones.

- **Primary (#0D284E):** Reserved for the Sidebar, Header backgrounds, and primary action buttons.
- **Secondary Blue (#3E5A7B):** Used for hover states, active navigation indicators, and sub-headers.
- **Gold Accent (#F2B705):** Signifies attention, pending statuses, and active highlights.
- **Semantic Colors:** Green (#16A34A) for "Completed/In-Stock" and Red (#DC2626) for "Alerts/Absences/Low Stock."
- **Typography:** Main text uses a near-black (#111827) for maximum contrast on white cards, with secondary text in a muted slate (#6B7280).

## Typography
This design system utilizes **Inter** for its exceptional legibility in data-heavy environments. The typographic scale is systematic, using semi-bold weights for data points and condensed labels for technical specifications (like tire dimensions or VIN numbers).

For mobile views, display sizes scale down to prevent text wrapping in narrow columns. All labels used in the workshop floor view (table headers, small badges) utilize a slightly increased letter-spacing to maintain readability under varied lighting conditions.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a fixed-width sidebar. 

- **Sidebar:** Fixed at 260px, utilizing a dark theme for permanent high-contrast navigation.
- **Main Content:** Adaptive container with a 24px margin.
- **Grid:** 12-column system for desktop, collapsing to a single column for mobile "Quick View" technician modes.
- **Rhythm:** An 8px linear scale (4, 8, 16, 24, 32) governs all padding and margins to ensure a tight, industrial alignment.

## Elevation & Depth
To maintain the "Industrial Tech" look, this design system avoids excessive shadows. Depth is primarily achieved through **Tonal Layers**:

1.  **Level 0 (Background):** #F1F3F5 (Light gray) acts as the canvas.
2.  **Level 1 (Cards/Tables):** #FFFFFF (White) with a subtle 1px border (#E5E7EB) and a soft, low-opacity shadow (0px 4px 6px rgba(0,0,0,0.05)).
3.  **Level 2 (Modals/Overlays):** Elevated with a more pronounced shadow (0px 10px 15px rgba(0,0,0,0.1)) to focus the user on critical inputs like "Add New Work Order."

Navigation elements in the sidebar use **Inner Glows** or left-border highlights in Gold (#F2B705) to show the active state, creating a "carved" or "lit" physical effect.

## Shapes
A consistent 8px-12px (Rounded) corner radius is applied to all UI components. This softens the industrial data while maintaining a professional software feel. 

- **Standard Buttons/Cards:** 8px (rounded-md).
- **KPI Cards/Large Containers:** 12px (rounded-lg).
- **Status Badges:** Fully pill-shaped (rounded-full) to distinguish them from interactive buttons.
- **Avatars:** Circular to contrast against the predominantly rectangular grid.

## Components

### Sidebar
The primary navigation uses the #0D284E background. Active links feature a #F2B705 left-border (4px wide) and white text. Inactive links use #3E5A7B for icons and text to maintain hierarchy.

### KPI Cards
White background with 12px rounding. They must include:
- A colored icon container (using a 10% opacity tint of the icon's semantic color).
- A large `display-md` value.
- A `label-bold` title in secondary text (#6B7280).

### Data Tables
Clean rows with #F1F3F5 bottom borders. Header cells use `label-bold` on a very light gray background. Row hover states should use a 5% opacity tint of the secondary blue to highlight the active record.

### Status Badges
Used in tables for "Pending," "Completed," and "Alert." These use high-contrast text on a light background (e.g., Green text #16A34A on a 10% opacity green background) for maximum scannability.

### Attendance List
Utilizes circular avatars with a 3px border indicating status (Green for "In Workshop", Red for "On Break/Absent"). Names are rendered in `body-md` bold.

### Input Fields
Bordered with 1px #D1D5DB. On focus, the border shifts to #3E5A7B with a 2px outer glow. Labels always sit above the input in `label-sm` weight.