# 🎨 OPD Queue Dashboard - Visual Component Reference

## Component Library & Style Guide

---

## 📦 Component Catalog

### 1. **Sidebar** 
```
Width: 300px
Height: 100vh (full screen)
Background: linear-gradient(180deg, #0f172a 0%, #0b1020 100%)
Shadow: 6px 0 20px rgba(0,0,0,0.25)
Overflow: auto (scrollable)

Sections:
├── Logo Section (32px 24px padding)
├── Role Card (20px 24px padding)
├── Department Selector (0 24px 22px)
├── Navigation Menu (flex: 1)
└── Online Status (18px 24px padding, border-top)

Colors:
- Background: #0f172a to #0b1020
- Text: rgba(255,255,255,0.7)
- Hover: rgba(255,255,255,0.06) + #67e8f9
- Active: #22d3ee with background
```

### 2. **Page Header**
```
Padding: 32px 40px
Border-bottom: 2px solid #e5e7eb
Box-shadow: 0 2px 8px rgba(0,0,0,0.04)
Background: #fff

Layout:
├── Left: Title + Subtitle
└── Right: Status Badges (horizontal)

Title: 36px, 900 weight, #0f172a
Subtitle: 15px, 400 weight, #64748b

Status Badges:
├── Orange: #fff7ed bg, #b45309 text (Waiting)
├── Blue: #e0f2fe bg, #0369a1 text (In Consultation)
└── Green: #ecfdf5 bg, #047857 text (Completed)
```

### 3. **Patient Card**
```
Dimensions: Full container width
Background: #fff
Border-left: 6px solid (status-based color)
Border-radius: 14px
Padding: 22px
Box-shadow: 0 4px 12px rgba(0,0,0,0.06)
Transition: all 300ms ease

Hover State:
- Box-shadow: 0 12px 28px rgba(0,0,0,0.12)
- Transform: translateY(-3px)

Layout:
├── Header (Flex: token + info + status)
├── Info Grid (3 columns, 18px gap)
├── Symptoms Box (styled, left border)
└── Action Buttons (flex, gap: 12px)

Status Colors:
├── Waiting (Orange): #f59e0b border-left
├── In Consultation (Blue): #3b82f6 border-left + light bg
├── Completed (Green): #10b981 border-left + opacity 0.9
└── Admitted (Purple): #8b5cf6 border-left
```

### 4. **Token Badge**
```
Size: 60x60px
Background: linear-gradient(135deg, #667eea, #764ba2)
Border-radius: 14px
Display: grid (place-items: center)
Font-size: 18px
Font-weight: 800
Color: #fff
Box-shadow: 0 6px 16px rgba(102,126,234,0.35)

Pseudo-Label (::after):
├── Content: "Token"
├── Position: absolute, bottom: -22px
├── Font-size: 10px
├── Color: #94a3b8
└── Letter-spacing: 0px
```

### 5. **Action Buttons**
```
Start Consultation:
- Gradient: linear-gradient(135deg, #3b82f6, #2563eb)
- Padding: 12px 18px
- Flex: 1 (full width)
- Hover: translateY(-2px) + shadow

Complete Consultation:
- Gradient: linear-gradient(135deg, #10b981, #059669)
- Padding: 12px 18px
- Hover: translateY(-2px) + shadow

Admit to Bed:
- Gradient: linear-gradient(135deg, #f59e0b, #d97706)
- Padding: 12px 18px
- Hover: translateY(-2px) + shadow

General Properties:
├── Border: none
├── Border-radius: 10px
├── Font-size: 13px
├── Font-weight: 700
├── Color: #fff
├── Cursor: pointer
├── Display: inline-flex
├── Gap: 8px (for icons)
├── Transition: all 300ms ease
└── Box-shadow: 0 2px 4px rgba(0,0,0,0.1)
```

### 6. **Status Badge Pill**
```
Padding: 8px 14px
Border-radius: 999px
Font-size: 12px
Font-weight: 700
Display: inline-block
Border: 1px solid (status-based)

Waiting:
├── Background: #fff7ed
├── Color: #b45309
└── Border: rgba(245,158,11,0.2)

In Consultation:
├── Background: #e0f2fe
├── Color: #0369a1
└── Border: rgba(59,130,246,0.2)

Completed:
├── Background: #ecfdf5
├── Color: #047857
└── Border: rgba(16,185,129,0.2)

Admitted:
├── Background: #f3e5f5
├── Color: #7b1fa2
└── Border: rgba(139,92,246,0.2)
```

### 7. **Modal Dialog**
```
Backdrop:
├── Position: fixed, top: 0, left: 0
├── Width: 100%, Height: 100%
├── Background: rgba(0,0,0,0.55)
├── Backdrop-filter: blur(3px)
└── Z-index: 2000

Content:
├── Background: #fff
├── Border-radius: 16px
├── Width: 90%, max-width: 420px
├── Box-shadow: 0 20px 60px rgba(0,0,0,0.25)
└── Animation: slideUp 300ms cubic-bezier(0.34, 1.56, 0.64, 1)

Header:
├── Padding: 28px 28px 20px
├── Border-bottom: 1px solid #e5e7eb
├── Display: flex (space-between)
└── Font-size: 22px, weight: 800

Body:
├── Padding: 24px 28px
├── Font-size: 15px
└── Color: #475569

Footer:
├── Padding: 20px 28px
├── Border-top: 1px solid #e5e7eb
├── Display: flex (gap: 12px)
└── Justify-content: flex-end

Buttons:
├── Cancel: #f3f4f6 bg, #374151 text, border
└── Confirm: linear-gradient(135deg, #667eea, #764ba2), #fff text
```

### 8. **Status Counter Badges**
```
Display: flex (align-items: center)
Padding: 12px 22px
Border-radius: 12px
Font-size: 14px
Font-weight: 800
Box-shadow: 0 2px 8px rgba(0,0,0,0.05)
Gap: 10px
Transition: all 300ms ease

Badge Dot:
├── Width: 9px
├── Height: 9px
├── Border-radius: 50%
├── Background: currentColor (inherits color)

Hover:
├── Transform: translateY(-2px)
└── Box-shadow: 0 6px 16px rgba(0,0,0,0.08)

Variants:
├── Waiting: gradient #fff7ed-#fef3c7, color #b45309
├── In Consult: gradient #e0f2fe-#d0e8fc, color #0369a1
└── Completed: gradient #ecfdf5-#d1f2eb, color #047857
```

### 9. **Empty State**
```
Container:
├── Text-align: center
├── Padding: 80px 40px
├── Display: flex (column, center)
└── Min-height: full viewport height

Icon:
├── Font-size: 84px
├── Margin-bottom: 24px
└── Opacity: 0.8

Heading:
├── Font-size: 28px
├── Font-weight: 800
├── Color: #0f172a
└── Margin-bottom: 12px

Description:
├── Font-size: 15px
├── Color: #64748b
├── Max-width: 340px
└── Margin-bottom: 32px

CTA Button:
├── Linked to /patient-registration
├── Styled as primary button
└── Color: #667eea
```

### 10. **Info Grid (Patient Details)**
```
Display: grid
Grid-template-columns: repeat(3, 1fr)
Gap: 18px
Margin-bottom: 18px
Padding-bottom: 18px
Border-bottom: 1px solid #f1f5f9

Each Item:
├── Display: flex (column)
├── Label: 10px, 800 weight, #94a3b8 (uppercase)
├── Value: 15px, 700 weight, #0f172a
└── Label margin-bottom: 8px

Tablet (1024px):
└── Grid-template-columns: repeat(2, 1fr)

Mobile (768px):
└── Grid-template-columns: 1fr
```

---

## 🎨 Color Reference

### Primary Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Dark Navy | `#0f172a` | Sidebar, main text |
| Off-Black | `#0b1020` | Sidebar gradient |
| White | `#fff` | Cards, text |
| Light Gray | `#f5f7fb` | Background |

### Status Colors
| Status | Color | Hex | Background |
|--------|-------|-----|------------|
| Waiting | Orange | `#f59e0b` | `#fff7ed` |
| In Consultation | Blue | `#3b82f6` | `#e0f2fe` |
| Completed | Green | `#10b981` | `#ecfdf5` |
| Admitted | Purple | `#8b5cf6` | `#f3e5f5` |

### Accent Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Cyan | `#22d3ee` | Sidebar highlights |
| Indigo | `#667eea` | Primary buttons |
| Violet | `#764ba2` | Gradients |
| Teal | `#a78bfa` | Logo gradient |

### Gray Scale
| Shade | Hex | Usage |
|-------|-----|-------|
| Gray-900 | `#0f172a` | Text, headings |
| Gray-700 | `#374151` | Secondary text |
| Gray-500 | `#6b7280` | Borders |
| Gray-300 | `#d1d5db` | Light borders |
| Gray-100 | `#f3f4f6` | Light backgrounds |
| Gray-50 | `#f9fafb` | Very light bg |

---

## 📐 Spacing Scale

### All Values in Pixels
```
xs:  8px  (small gaps, internal padding)
sm:  12px (button padding, card elements)
md:  16px (card spacing)
lg:  20px (card padding)
xl:  24px (sidebar padding)
2xl: 32px (page header padding)
3xl: 40px (page horizontal padding)
```

### Common Combinations
```
Buttons:      12px 18px (vertical, horizontal)
Card Padding: 22px
Modal Header: 28px 28px 20px
Sidebar Item: 13px 24px (vertical, horizontal)
Info Grid:    Gap 18px
Button Gap:   12px
```

---

## 📝 Typography Reference

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### Font Weights
```
500 - Reserved
600 - Secondary content, labels
700 - Primary content, info values
800 - Headers, badges
900 - Main logo, page titles
```

### Font Sizes
```
36px - Page title (h1)
30px - Sidebar logo
28px - Modal header
22px - Section headers
17px - Patient names
15px - Info values, body text
14px - Badge text, button text
13px - Navigation items
12px - Status pills
10px - Labels, badges
```

### Line Heights
```
1.0 - Badges, single line
1.2 - Headings
1.3 - Patient info
1.4 - Subtitles
1.5 - Body text
1.6 - Symptoms, descriptions
```

---

## 🔄 Animations Catalog

### CSS Transitions
```css
/* Default smooth transition */
transition: all 300ms ease;

/* Faster interaction */
transition: all 250ms ease;

/* Bounce effect */
transition: all 300ms ease cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Keyframe Animations
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
  /* Duration: 2000ms infinite */
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
  /* Duration: 250ms ease */
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
  /* Duration: 250ms ease */
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
  /* Duration: 300ms cubic-bezier(0.34, 1.56, 0.64, 1) */
}
```

### Common Transforms
```css
/* Hover elevation */
transform: translateY(-3px);  /* Cards */
transform: translateY(-2px);  /* Buttons, badges */
transform: translateY(0);     /* Active state */

/* Rotations */
transform: rotate(0deg);      /* Default */

/* Scaling */
transform: scale(0.98);       /* Active button press */
```

---

## 🔲 Breakpoints & Responsive

### Desktop
```css
@media (min-width: 1025px) {
  /* Full layout: Sidebar + Content */
  .sidebar { width: 300px; }
  .patient-info { grid-template-columns: repeat(3, 1fr); }
}
```

### Tablet
```css
@media (max-width: 1024px) {
  /* Adjusted grid */
  .patient-info { grid-template-columns: repeat(2, 1fr); }
}
```

### Mobile
```css
@media (max-width: 768px) {
  /* Stacked layout */
  .sidebar { flex-direction: row; overflow-x: auto; }
  .patient-info { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .btn { width: 100%; }
}
```

---

## 🎯 Shadow System

| Type | CSS | Usage |
|------|-----|-------|
| Subtle | `0 2px 4px rgba(0,0,0,0.1)` | Button default |
| Card | `0 4px 12px rgba(0,0,0,0.06)` | Patient card |
| Hover | `0 12px 28px rgba(0,0,0,0.12)` | Card hover |
| Modal | `0 20px 60px rgba(0,0,0,0.25)` | Dialog |
| Sidebar | `6px 0 20px rgba(0,0,0,0.25)` | Left edge |

---

## 🎭 Interactive States

### Button States
```
Default:  background-color, box-shadow
Hover:    transform: translateY(-2px), enhanced shadow
Active:   transform: translateY(0), reduced shadow
Disabled: opacity: 0.5, cursor: not-allowed
Focus:    outline: 2px solid accent-color
```

### Card States
```
Default:  normal shadow, position
Hover:    enhanced shadow, translateY(-3px)
Active:   same as hover (click)
Focus:    outline or border highlight
```

### Modal States
```
Hidden:   display: none, opacity: 0
Showing:  display: flex, animation: slideUp
```

---

## 📊 Component Checklist

- [x] Sidebar (navigation, branding, role switch)
- [x] Page Header (title, status badges)
- [x] Patient Cards (token, info, actions)
- [x] Action Buttons (Start, Complete, Admit)
- [x] Status Badges (color-coded)
- [x] Modal Dialogs (confirmations)
- [x] Info Grid (3-column patient details)
- [x] Empty State (no patients message)
- [x] Responsive Layout (all breakpoints)
- [x] Animations (smooth transitions)
- [x] Hover Effects (interactive feedback)
- [x] Focus States (accessibility)

---

## 🎓 Design Guidelines

1. **Consistency**: Use defined colors, fonts, spacing consistently
2. **Hierarchy**: Establish clear visual hierarchy with typography
3. **Accessibility**: Maintain contrast ratios, clear labels
4. **Performance**: CSS animations (hardware-accelerated)
5. **Responsiveness**: Mobile-first approach
6. **Medical Theme**: Professional colors, clean layout
7. **Feedback**: All interactive elements provide feedback
8. **Efficiency**: Icons and color for quick scanning

---

## 🔗 Cross-References

- **Colors**: See DESIGN_SPECIFICATIONS.md
- **Layout**: See IMPLEMENTATION_GUIDE.md
- **Features**: See OPD_QUEUE_DESIGN_SUMMARY.md
- **Code**: See templates/opd_queue.html (lines 1-173 CSS)

---

**Last Updated**: January 8, 2025  
**Version**: 2.0 - Complete Visual Reference  
**Status**: ✅ Production Ready
