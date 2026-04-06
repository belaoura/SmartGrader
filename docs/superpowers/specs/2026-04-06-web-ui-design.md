# SmartGrader Web UI -- Design Specification

**Date:** 2026-04-06
**Status:** Approved
**Depends on:** Sub-Project 1 (Code Restructuring) -- complete
**Design System:** design-system/smartgrader/MASTER.md

---

## 1. Overview

Build a modern web frontend for SmartGrader replacing the legacy PyQt5 desktop UI. The frontend consumes the Flask REST API (already implemented, 12 endpoints, 40 passing tests). The UI follows a data-dense dashboard style with academic typography, light-first theme with dark mode, and RTL Arabic support.

### Goals
- Professional, polished UI suitable for a PFE defense demo
- Responsive: works on desktop (1440px), laptop (1024px), tablet (768px), mobile (375px)
- Light-first with dark mode toggle
- Trilingual support: French, Arabic (RTL), English
- All 9 pages from the approved spec implemented

### Constraints
- Single-developer project (PFE scope)
- Flask backend already done -- frontend is a separate Vite project in `frontend/`
- No SSR needed -- Vite SPA with proxy to Flask

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | React 18 | UI components |
| Build | Vite | Dev server, bundling, HMR |
| Styling | Tailwind CSS | Utility-first CSS |
| Components | shadcn/ui | Pre-built accessible components |
| Icons | Lucide React | SVG icon library |
| Routing | React Router v6 | Client-side navigation |
| Server State | TanStack Query (React Query) | API calls, caching, refetching |
| Charts | Recharts | Bar, pie, line charts |
| Fonts | Crimson Pro + Atkinson Hyperlegible | Academic typography (Google Fonts) |
| RTL | tailwindcss-rtl | Automatic RTL margin/padding flipping |

---

## 3. Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── main.jsx                  # Entry point, providers
│   ├── App.jsx                   # Router + AppLayout
│   ├── index.css                 # Tailwind + Google Fonts + CSS variables
│   ├── lib/
│   │   ├── api.js                # Fetch wrapper for Flask API
│   │   ├── utils.js              # shadcn/ui cn() utility
│   │   └── query-client.js       # TanStack Query config
│   ├── hooks/
│   │   ├── use-exams.js          # useQuery/useMutation for exams
│   │   ├── use-students.js       # useQuery/useMutation for students
│   │   ├── use-results.js        # useQuery for results
│   │   └── use-theme.js          # Dark/light mode with localStorage
│   ├── components/
│   │   ├── ui/                   # shadcn/ui primitives (auto-generated)
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx       # Left navigation sidebar
│   │   │   ├── TopBar.jsx        # Top header bar
│   │   │   └── AppLayout.jsx     # Shell: Sidebar + TopBar + content
│   │   ├── dashboard/
│   │   │   ├── StatCard.jsx      # KPI card (icon, value, label)
│   │   │   └── Charts.jsx        # Recharts wrappers (bar, pie)
│   │   ├── exams/
│   │   │   ├── ExamList.jsx      # Exam data table
│   │   │   ├── ExamForm.jsx      # Create/edit exam dialog
│   │   │   └── QuestionBuilder.jsx # Dynamic question + choices form
│   │   ├── scanner/
│   │   │   ├── UploadZone.jsx    # Drag-and-drop file upload
│   │   │   └── ScanResults.jsx   # Grading result display
│   │   ├── students/
│   │   │   ├── StudentList.jsx   # Student data table
│   │   │   └── StudentForm.jsx   # Add student dialog
│   │   └── results/
│   │       ├── ResultsTable.jsx  # Per-exam results table
│   │       └── ExportButton.jsx  # CSV/PDF export
│   └── pages/
│       ├── Dashboard.jsx         # Statistics overview
│       ├── Exams.jsx             # Exam management
│       ├── ExamDetail.jsx        # Single exam with questions
│       ├── Scanner.jsx           # Upload + scan + grade
│       ├── Students.jsx          # Student roster
│       ├── Results.jsx           # Results + analytics
│       └── Settings.jsx          # Theme, language, thresholds
├── components.json               # shadcn/ui config
├── tailwind.config.js            # Design system tokens
├── vite.config.js                # Proxy /api → Flask :5000
├── package.json
└── index.html
```

---

## 4. Layout

### AppLayout Shell

```
┌──────────────────────────────────────────────────────┐
│  TopBar (h-16, fixed top, full width)                 │
│  [☰] [SmartGrader]                    [🌙] [FR] [👤] │
├────────────┬─────────────────────────────────────────┤
│  Sidebar   │  Content Area (scrollable)               │
│  (w-64)    │                                          │
│  fixed     │  <Page component rendered here>          │
│  left      │                                          │
└────────────┴─────────────────────────────────────────┘
```

### Sidebar Behavior
- Desktop (>= 1024px): fixed, 256px wide, always visible
- Tablet (768-1023px): collapsed to 64px (icons only), hover to expand
- Mobile (< 768px): hidden, slide-over drawer triggered by hamburger

### Sidebar Items
| Icon | Label | Route |
|------|-------|-------|
| LayoutDashboard | Dashboard | `/` |
| FileText | Exams | `/exams` |
| ScanLine | Scanner | `/scanner` |
| Users | Students | `/students` |
| BarChart3 | Results | `/results` |
| Settings | Settings | `/settings` |

Active item: accent background (`bg-green-600/10 text-green-600` light, `bg-green-500/10 text-green-500` dark).

### TopBar
- Left: hamburger toggle (mobile only) + "SmartGrader" in Crimson Pro semibold
- Right: theme toggle (Sun/Moon icon), language dropdown (FR/AR/EN), avatar placeholder
- Height: 64px

---

## 5. Theme System

### Light Mode (Default)
| Role | Value |
|------|-------|
| Background | `#FFFFFF` (page), `#F8FAFC` (sidebar, cards) |
| Text | `#0F172A` (primary), `#475569` (secondary) |
| Accent | `#16A34A` (green-600) |
| Border | `#E2E8F0` |
| Card | `#FFFFFF` with `shadow-sm` |

### Dark Mode
| Role | Value |
|------|-------|
| Background | `#020617` (page), `#0F172A` (sidebar, cards) |
| Text | `#F8FAFC` (primary), `#94A3B8` (secondary) |
| Accent | `#22C55E` (green-500) |
| Border | `#1E293B` |
| Card | `#0F172A` with `shadow-md` |

Implementation: CSS variables on `:root` and `[data-theme="dark"]`. The `use-theme.js` hook reads/writes `localStorage("theme")` and toggles `data-theme` attribute on `<html>`.

### Typography
- Headings: Crimson Pro (400-700), academic/scholarly mood
- Body: Atkinson Hyperlegible (400, 700), maximum readability
- Base size: 16px body, responsive scale

### RTL Support
- Language selector toggles `dir="rtl"` on `<html>`
- `tailwindcss-rtl` plugin auto-flips `ml-*`/`mr-*`, `pl-*`/`pr-*`
- Sidebar moves to right side in RTL
- Arabic font fallback in Tailwind config

---

## 6. Pages

### 6.1 Dashboard (`/`)
- **4 KPI stat cards** (top row, responsive grid): Total Exams, Total Questions, Total Students, Average Score
  - Each card: Lucide icon (muted), large value, label below, subtle background
- **2-column chart grid** (below cards):
  - Left: Recharts BarChart -- "Results by Exam" (exam title on X, avg score on Y)
  - Right: Recharts PieChart -- "Pass/Fail Distribution" (green/red slices)
- **Recent Results table** (bottom): last 10 graded results, columns: Student, Exam, Score, Percentage, Date

API calls: `GET /api/exams`, `GET /api/students`, `GET /api/results/exam/:id`

### 6.2 Exams (`/exams`)
- Header: "Exams" title + "New Exam" primary button
- shadcn/ui DataTable: Title, Subject, Date, Questions (count), Total Marks, Actions
- Actions column: Edit (pencil icon), Delete (trash icon with confirm dialog), Generate Sheet (download icon)
- "New Exam" button opens ExamForm Dialog: title (required), subject, date picker, total marks
- Row click navigates to `/exams/:id`

API calls: `GET /api/exams`, `POST /api/exams`, `PUT /api/exams/:id`, `DELETE /api/exams/:id`

### 6.3 Exam Detail (`/exams/:id`)
- Exam info header: title, subject, date, stat badges (questions count, total marks)
- "Add Question" primary button + "Generate Answer Sheet" secondary button
- Questions list (scrollable): each question card shows:
  - Question number + text + marks badge
  - Choices list: A/B/C/D with correct answer highlighted green
  - Edit/delete icons per question
- QuestionBuilder: Dialog with dynamic form
  - Question text textarea
  - Marks number input
  - Dynamic choices (start with 4, add/remove up to 6)
  - Radio button to mark correct answer
  - Save button

API calls: `GET /api/exams/:id`, `GET /api/exams/:id/questions`, `POST /api/exams/:id/questions`

Note: "Generate Answer Sheet" requires adding a new endpoint `POST /api/exams/:id/generate` to the Flask backend (wrapping the legacy sheet_generator). This will be added as a task in the implementation plan.

### 6.4 Scanner (`/scanner`)
- Step 1: Select exam from dropdown (required)
- Step 2: UploadZone -- dashed border drag-and-drop area, accepts PDF/PNG/JPG, shows file preview
- Step 3: "Scan & Grade" button (disabled until file + exam selected)
- Loading state: progress spinner with "Scanning..." text
- ScanResults (after grading):
  - Score summary card: obtained/total marks, percentage, large text
  - Per-question breakdown table: Q#, Detected Answer, Correct Answer, Status (check/x icon)
  - Color-coded rows: green = correct, red = incorrect, amber = unanswered

API calls: `POST /api/scan/upload` (multipart)

### 6.5 Students (`/students`)
- Header: "Students" + "Add Student" button
- shadcn/ui DataTable: Name, Matricule, Email, Actions (view/delete)
- "Add Student" Dialog: name (required), matricule (required, unique), email
- Future: "Import CSV" button (parses CSV, bulk POST)

API calls: `GET /api/students`, `POST /api/students`

### 6.6 Results (`/results`)
- Filter bar: exam selector dropdown (defaults to "All Exams")
- ResultsTable: Student Name, Matricule, Exam, Score, Percentage, Graded At
- Sortable columns (click header to sort)
- Grade distribution bar chart (Recharts): X = score ranges (0-25%, 25-50%, 50-75%, 75-100%), Y = student count
- Export buttons: "Export CSV", "Export PDF"

API calls: `GET /api/results/exam/:id`

### 6.7 Settings (`/settings`)
- Appearance section: theme toggle switch (light/dark), language radio group (FR/AR/EN)
- Scanner section: fill threshold slider (0-100, default 50), display current value
- About section: app version, project info

Settings stored in localStorage (no backend persistence needed).

---

## 7. API Integration

### Fetch Wrapper (`lib/api.js`)
```javascript
const API_BASE = "/api";

async function fetchAPI(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Request failed");
  }
  return response.json();
}
```

### TanStack Query Hooks Pattern
Each hook file exports useQuery and useMutation hooks:
```javascript
// hooks/use-exams.js
export function useExams() {
  return useQuery({ queryKey: ["exams"], queryFn: () => fetchAPI("/exams") });
}
export function useCreateExam() {
  return useMutation({
    mutationFn: (data) => fetchAPI("/exams", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries(["exams"]),
  });
}
```

### Vite Proxy
```javascript
// vite.config.js
server: {
  proxy: { "/api": "http://localhost:5000" }
}
```

---

## 8. Design System Integration

From `design-system/smartgrader/MASTER.md`:

- **Style:** Data-Dense Dashboard -- KPI cards, data tables, minimal padding, grid layout
- **Typography:** Crimson Pro (headings) + Atkinson Hyperlegible (body)
- **Icons:** Lucide React (no emojis)
- **Effects:** hover tooltips, row highlighting, smooth transitions (150-300ms), skeleton loaders
- **Anti-patterns to avoid:** ornate design, no filtering, emojis as icons, missing cursor:pointer, invisible focus states

### shadcn/ui Components Used
- Button, Card, Dialog, Table, Input, Select, Label, Badge, Dropdown Menu
- Tabs, Switch, Slider, Separator, Skeleton, Toast

### Pre-Delivery Checklist
- [ ] No emojis as icons (Lucide SVGs only)
- [ ] cursor-pointer on all clickable elements
- [ ] Hover states with transitions (150-300ms)
- [ ] Contrast ratio 4.5:1 minimum
- [ ] Visible focus states for keyboard nav
- [ ] prefers-reduced-motion respected
- [ ] Responsive at 375px, 768px, 1024px, 1440px

---

## 9. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Theme default | Light-first | Academic context, easier for long grading sessions |
| Layout | Sidebar + TopBar | Dashboard-style, shows all nav at once |
| Build tool | Vite | Fast HMR, lightweight, standard for React 2026 |
| Charts | Recharts | React-native, works well with shadcn/ui |
| State management | TanStack Query + useState | API-driven app, no global store needed |
| Icons | Lucide React | Matches design system requirement (SVG, no emoji) |
| RTL | tailwindcss-rtl | Automatic flipping, minimal manual work |
| Font | Crimson Pro + Atkinson Hyperlegible | Academic mood, maximum readability |
