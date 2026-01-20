# 🎨 Patient Dashboard - Visual Design Reference

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  PATIENT DASHBOARD - MEDIFLOW HOSPITAL MANAGEMENT SYSTEM        │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────┐                                                 │
│  │  SIDEBAR   │  ┌──────────────────────────────────────────┐   │
│  │            │  │         DASHBOARD HEADER                │   │
│  │ MEDIFLOW   │  │  Patient Dashboard                       │   │
│  │            │  │  Track your health information...        │   │
│  ├────────────┤  │                           [Hospital Dash]│   │
│  │  AD Profile│  └──────────────────────────────────────────┘   │
│  │  Switch Ro │                                                 │
│  │   ▼        │  ┌────────────┬────────────┬─────────┬────────┐ │
│  ├────────────┤  │   PATIENTS │  IN QUEUE  │ BEDS OCC│TOTAL BD│ │
│  │  HOME      │  │   STAT 1   │   STAT 2   │ STAT 3  │ STAT 4 │ │
│  │  BED MGMT  │  └────────────┴────────────┴─────────┴────────┘ │
│  │  REGISTER  │  ┌──────────────────────────────────────────┐   │
│  │  OPD QUEUE │  │  RECENT PATIENTS TABLE                  │   │
│  │            │  │  [Search...] [Dept Filter]              │   │
│  │            │  ├──────────────────────────────────────────┤   │
│  │ ● Online   │  │ Name | Age | Dept | Status | Time       │   │
│  └────────────┘  │ ─────────────────────────────────────────│   │
│                  │ John |  45 | Gen  | Admitted | 10:30    │   │
│                  │ Sarah|  32 | Cardi| Waiting  | 10:45    │   │
│                  │ Mike |  60 | Ortho| Completed| 11:00    │   │
│                  │ ...                                      │   │
│                  ├──────────────────────────────────────────┤   │
│                  │  « Previous  Page 1 of 5  Next »         │   │
│                  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Color Palette

### Primary Colors
```
Sidebar Background:  Linear Gradient #0f172a → #1a1f3a (Dark Blue)
Primary Accent:      #667eea (Medium Blue)
Secondary Accent:    #764ba2 (Purple)
```

### Stat Card Icons
```
Stat 1 (👥 Patients):     #3b82f6 (Blue)
Stat 2 (⏳ Queue):        #f59e0b (Yellow)
Stat 3 (🛏️ Beds):        #10b981 (Green)
Stat 4 (🏥 Total):       #8b5cf6 (Purple)
```

### Status Badges
```
Admitted:    Background #10b981/15%, Text #047857 (Green)
Waiting:     Background #f59e0b/15%, Text #92400e (Yellow)
Completed:   Background #3b82f6/15%, Text #1e40af (Blue)
Discharge:   Background #8b5cf6/15%, Text #6b21a8 (Purple)
```

### Text Colors
```
Primary Text:   #0f172a (Very Dark Blue)
Secondary Text: #2c3e50 (Dark Blue-Gray)
Tertiary Text:  #64748b (Medium Gray)
Light Text:     #94a3b8 (Light Gray)
Muted Text:     #cbd5e1 (Very Light Gray)
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
             'Helvetica Neue', Arial, sans-serif;
```

### Font Sizes
```
Page Title (h1):     32px (28px tablet, 22px mobile)
Section Title (h2):  20px
Card Value:          36px (28px tablet, 24px mobile)
Card Label:          14px
Table Header:        11px (uppercase)
Table Row:           13px
```

### Font Weights
```
Bold:              700
Extra Bold:        800
Semi-Bold:         600
Regular:           500
```

## Spacing System

### Padding
```
Header Section:    40px (32px tablet, 24px mobile)
Card Section:      36px (28px tablet, 20px mobile)
Table Section:     0 48px 48px (0 36px 36px tablet)
Card Padding:      28px (24px tablet, 20px mobile)
Cell Padding:      18px (14px tablet, 12px mobile)
```

### Gaps & Margins
```
Stats Grid Gap:    24px (16px tablet, 12px mobile)
Control Gap:       16px
Stat Icon Margin:  16px bottom
```

## Border Radius

```
Buttons & Inputs:   10px
Cards & Containers: 16px
User Avatar:        10px (Sidebar), 20px (Badges)
Table Container:    16px (top), 0px (bottom)
```

## Shadow System

```
Light Shadow:      0 2px 4px rgba(0,0,0,0.08)
Medium Shadow:     0 8px 24px rgba(0,0,0,0.08)
Strong Shadow:     0 16px 32px rgba(0,0,0,0.12)
Hover Shadow:      0 16px 32px rgba(0,0,0,0.12)
Focus Shadow:      0 0 0 3px rgba(102,126,234,0.1)
```

## Glassmorphism Effects

### Card Background
```css
background: rgba(255, 255, 255, 0.85);
border: 1px solid rgba(255, 255, 255, 0.6);
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px);
```

### Hover State
```css
background: rgba(255, 255, 255, 0.95);
border-color: rgba(255, 255, 255, 0.8);
```

## Animations

### Fade In (Page Load)
```css
Animation: fadeIn 0.6s ease-out
From: opacity 0, translate Y 20px
To: opacity 1, translate Y 0
```

### Hover Lift (Cards)
```css
Transform: translateY(-8px)
Transition: all 0.3s ease
Shadow: 0 16px 32px rgba(0,0,0,0.12)
```

### Dropdown Slide
```css
Animation: slideDown 0.25s ease
From: opacity 0, translate Y -8px
To: opacity 1, translate Y 0
```

### Pulse (Status Dot)
```css
Animation: pulse 2s ease-in-out infinite
0%, 100%: opacity 1
50%: opacity 0.5
```

## Responsive Grid System

### Desktop (1400px+)
```
Stats Grid:  4 columns (repeat(4, 1fr))
Sidebar:     280px width, full height
Header:      Full width with flex layout
Table:       Full responsive width
```

### Laptop (1024px - 1399px)
```
Stats Grid:  2 columns (repeat(2, 1fr))
Sidebar:     240px width
Header:      Reduced padding
Table:       Scrollable
```

### Tablet (768px - 1023px)
```
Stats Grid:  2 columns
Sidebar:     Horizontal top bar, 60px height
Nav Items:   Horizontal flex layout
Header:      Stacked flex-direction column
Table:       Horizontally scrollable
Controls:    Stacked vertically
```

### Mobile (< 768px)
```
Stats Grid:  1 column
Sidebar:     Removed (top nav only)
Header:      Padding 18px, centered
Table:       Full width, horizontal scroll
Search/Filter: Full width stacked
```

## Interactive States

### Button States
```
Default:   Background rgba(255,255,255,0.06), Border rgba(255,255,255,0.1)
Hover:     Background rgba(255,255,255,0.1), Border rgba(255,255,255,0.2)
Active:    Border-color gradient, Background rgba(102,126,234,0.15)
```

### Input States
```
Default:   Border #e2e8f0
Focus:     Border #667eea, Shadow 0 0 0 3px rgba(102,126,234,0.1)
Hover:     Border #667eea
```

### Table Row States
```
Default:   Background transparent
Hover:     Background rgba(99,102,241,0.04)
```

## Component Specifications

### Stat Card
```
Width:         100% (grid item)
Height:        Auto (min ~140px)
Padding:       28px
Background:    Glassmorphic
Border:        1px solid rgba(255,255,255,0.6)
Border Radius: 16px
Box Shadow:    0 8px 24px rgba(0,0,0,0.08)
Hover:         -8px transform, stronger shadow
```

### Table
```
Width:         100%
Border:        None (card bordered)
Header BG:     Linear gradient #f8f9fc → #f5f6fa
Header Border: 2px solid #e2e8f0
Row Border:    1px solid #f1f5f9
Cell Padding:  18px (responsive)
```

### Search Box
```
Width:         240px (100% on mobile)
Height:        44px (11px padding)
Border:        1px solid #e2e8f0
Border Radius: 10px
Padding:       11px 16px 11px 40px (icon space)
Icon:          14px, #94a3b8, left 14px
```

### Pagination
```
Button Padding:  8px 12px
Border Radius:   8px
Font Size:       12px
Font Weight:     600
Default Border:  #e2e8f0
Active BG:       #667eea
Active Color:    #fff
Disabled:        opacity 0.5
```

## Accessibility

### Color Contrast
- Text on background: >= 4.5:1 (WCAG AA)
- Buttons and links: >= 3:1 (WCAG AA)

### Focus States
- Visible focus ring on interactive elements
- Blue accent color for focus indication
- Sufficient padding around focus targets

### Semantic HTML
- Proper heading hierarchy (h1 → h2)
- Table semantic markup
- Form labels and inputs properly associated
- Icon accessibility with proper aria labels

## Browser Compatibility

### Supported Features
```
CSS Grid:           All modern browsers
Flexbox:            All modern browsers
Backdrop Filter:    Chrome 76+, Safari 9+, Firefox 103+
CSS Transforms:     All modern browsers
CSS Animations:     All modern browsers
CSS Variables:      Chrome 49+, Firefox 31+, Safari 9.1+
```

### Fallbacks
```
Backdrop Filter:    Opacity fallback
CSS Grid:           Flexbox fallback
Transforms:         No-transform fallback
```
