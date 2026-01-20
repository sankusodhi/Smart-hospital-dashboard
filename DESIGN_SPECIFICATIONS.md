# OPD Queue Dashboard - Design Specifications & Color Scheme

## 📋 Color Palette

### Primary Colors
| Color | Hex | Usage | Purpose |
|-------|-----|-------|---------|
| Dark Navy | `#0f172a` | Sidebar background, main text | Trust, professionalism |
| Off-Black | `#0b1020` | Sidebar gradient end | Depth, contrast |
| White | `#fff` | Card backgrounds, text | Clarity, cleanliness |
| Light Gray | `#f5f7fb` | Page background | Subtle contrast |

### Status Colors
| Status | Color | Hex | Background Hex | Use Case |
|--------|-------|-----|-----------------|----------|
| Waiting | Orange | `#b45309` | `#fff7ed` | Patient needs attention |
| In Consultation | Blue | `#0369a1` | `#e0f2fe` | Active treatment |
| Completed | Green | `#047857` | `#ecfdf5` | Successfully discharged |
| Admitted | Purple | `#7b1fa2` | `#f3e5f5` | Hospitalized |

### Accent Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Cyan | `#22d3ee` | Sidebar highlights, active states |
| Purple | `#a78bfa` | Gradient accents, interactive elements |
| Indigo | `#667eea` | Buttons, badges, primary actions |
| Violet | `#764ba2` | Gradient combinations |

---

## 🎨 Typography Scale

| Element | Font Size | Font Weight | Line Height | Letter Spacing |
|---------|-----------|-------------|-------------|-----------------|
| **Sidebar Logo (Main)** | 30px | 900 | 1.2 | 0px |
| **Sidebar Logo (Sub)** | 10px | 700 | 1.0 | 2px (upper) |
| **Page Title** | 36px | 900 | 1.2 | 0px |
| **Page Subtitle** | 15px | 400 | 1.4 | 0px |
| **Patient Name** | 17px | 700 | 1.3 | 0px |
| **Patient Age/Meta** | 13px | 600 | 1.3 | 0px |
| **Info Labels** | 10px | 800 | 1.0 | 0.8px (upper) |
| **Info Values** | 15px | 700 | 1.3 | 0px |
| **Status Badge** | 12px | 700 | 1.0 | 0px |
| **Symptoms Text** | 14px | 400 | 1.6 | 0px |
| **Button Text** | 13-14px | 700 | 1.0 | 0px |
| **Badge Counter** | 14px | 800 | 1.0 | 0px |

---

## 📐 Spacing System

### Padding
| Size | Value | Usage |
|------|-------|-------|
| xs | 8px | Small internal spacing |
| sm | 12px | Button padding, modal content |
| md | 16px | Card internal spacing |
| lg | 20px | Card spacing |
| xl | 24px | Sidebar/header padding |
| 2xl | 32px | Section padding |

### Gaps & Margins
| Size | Value | Usage |
|------|-------|-------|
| xs | 8px | Button groups |
| sm | 12px | Card elements |
| md | 18px | Patient card sections |
| lg | 20px | Queue container |
| xl | 40px | Page sides |

---

## 🎯 Component Dimensions

### Sidebar
- Width: `300px`
- Logo padding: `32px 24px`
- Role avatar: `50x50px`
- Role switch button: Full width, `11px` vertical padding
- Nav items: `13px` vertical, `24px` horizontal padding

### Page Header
- Height: Auto (min-height ~100px on desktop)
- Padding: `32px 40px`
- Title font-size: `36px`
- Status badges: `12px 22px` padding

### Patient Cards
- Background: White with gradient accent (::before pseudo-element)
- Border-left: `6px` solid (color varies by status)
- Border-radius: `14px`
- Padding: `22px`
- Token badge: `60x60px` with `14px` border-radius
- Hover elevation: `3px` translateY

### Buttons
- Padding: `12px 18px` (standard), `12px 22px` (confirm)
- Border-radius: `10px`
- Font-weight: `700`
- Hover: `-2px` translateY + enhanced shadow
- Active: `0px` translateY (returns to baseline)

### Modals
- Width: `90%` (max `420px`)
- Border-radius: `16px`
- Header padding: `28px 28px 20px`
- Body padding: `24px 28px`
- Footer padding: `20px 28px`
- Shadow: `0 20px 60px rgba(0,0,0,0.25)`

---

## 🌈 Gradient Definitions

### Logo Gradient
```css
background: linear-gradient(135deg, #67e8f9 0%, #a78bfa 100%);
```
Cyan to purple, 45° angle for diagonal appeal

### Button Gradients
```css
/* Start Button (Blue) */
background: linear-gradient(135deg, #3b82f6, #2563eb);

/* Complete Button (Green) */
background: linear-gradient(135deg, #10b981, #059669);

/* Admit Button (Amber) */
background: linear-gradient(135deg, #f59e0b, #d97706);

/* Switch Role (Indigo) */
background: linear-gradient(135deg, #667eea, #764ba2);
```

### Status Badge Gradients
```css
/* Waiting (Orange) */
background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%);

/* In Consultation (Blue) */
background: linear-gradient(135deg, #e0f2fe 0%, #d0e8fc 100%);

/* Completed (Green) */
background: linear-gradient(135deg, #ecfdf5 0%, #d1f2eb 100%);
```

---

## 🎭 Shadow System

| Type | CSS | Usage |
|------|-----|-------|
| Subtle | `0 2px 4px rgba(0,0,0,0.1)` | Button default |
| Card | `0 4px 12px rgba(0,0,0,0.06)` | Patient card |
| Hover | `0 12px 28px rgba(0,0,0,0.12)` | Card on hover |
| Modal | `0 20px 60px rgba(0,0,0,0.25)` | Dialog boxes |
| Sidebar | `6px 0 20px rgba(0,0,0,0.25)` | Sidebar edge |

---

## 🔄 Animation Timing

| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| Hover lift | 300ms | ease | Buttons, cards |
| Color transition | 300ms | ease | Status changes |
| Modal enter | 300ms | cubic-bezier(0.34, 1.56, 0.64, 1) | Dialog appearance |
| Backdrop fade | 250ms | ease | Modal backdrop |
| Dropdown | 250ms | ease | Role menu |
| Pulse | 2000ms | infinite | Status indicator |

---

## 📱 Responsive Breakpoints

### Desktop (1024px+)
- Sidebar: `300px` fixed width
- Patient info: 3-column grid
- Status badges: Horizontal layout
- Full navigation visible

### Tablet (768px - 1023px)
- Patient info: 2-column grid
- Full layout maintained
- Moderate padding adjustments

### Mobile (<768px)
- Sidebar: Horizontal scroll, `auto` height
- Patient info: 1-column grid
- Action buttons: Stacked full-width
- Padding reduced to `16-24px`
- Navigation hidden (only roles visible in sidebar)
- Page header: Vertical layout

---

## ✨ Special Effects

### Token Badge Pseudo-Label
```css
.token-badge::after {
  content: 'Token';
  position: absolute;
  bottom: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
  white-space: nowrap;
}
```

### Card Accent (Radial Gradient)
```css
.patient-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(102,126,234,0.05) 0%, transparent 70%);
  border-radius: 0 14px 0 40px;
}
```

### Status Messages with Icons
```css
.completed-message::before {
  content: '✓';
  font-weight: 900;
  font-size: 16px;
}
```

---

## 🎯 Key Design Principles

1. **Visual Hierarchy**: Large, bold titles → medium info → small labels
2. **Color Semantics**: Orange=action, Blue=active, Green=success, Purple=admitted
3. **Micro-interactions**: Hover feedback on clickable elements
4. **Whitespace**: Generous padding for breathing room
5. **Medical Aesthetic**: Trust-building colors, professional layout
6. **Accessibility**: High contrast, clear iconography, no color-only information
7. **Performance**: CSS-based animations (no JS-heavy effects)
8. **Consistency**: Unified shadows, rounded corners, spacing patterns

---

## 📊 Usage Example: Patient Card Variations

### Waiting Patient
```
Border: Orange (#f59e0b) left border
Background: White with subtle orange radial gradient
Card class: .patient-card.waiting
Status badge: Orange pill with "Waiting" text
Actions: "Start" button (blue)
```

### In Consultation
```
Border: Blue (#3b82f6) left border
Background: Light blue gradient (#f8faff)
Card class: .patient-card.in-consultation
Status badge: Blue pill with "In Consultation" text
Actions: "Complete" (green) + "Admit" (amber) buttons
```

### Completed
```
Border: Green (#10b981) left border
Background: White with reduced opacity (0.9)
Card class: .patient-card.completed
Status badge: Green pill with "Completed" text
Actions: Message "✓ Consultation Completed"
```

### Admitted
```
Border: Purple (#8b5cf6) left border
Background: White
Card class: .patient-card.admitted
Status badge: Purple pill with "Admitted" text
Actions: Message "✓ Patient Admitted to Bed"
```

---

**Design Version**: 2.0 - Enhanced Modern Medical Theme  
**Last Updated**: 2025-01-08  
**Compatibility**: All modern browsers (Chrome, Firefox, Safari, Edge)
