import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import {
  Archive, Monitor, Globe, Database, ScanLine, ArrowRight,
  Terminal, FileCode, Brain, ChevronDown, ChevronRight,
  CheckCircle2, Clock, Layers, AlertTriangle, Code2,
} from "lucide-react";

const LEGACY_FILES = [
  { file: "main.py",              role: "Application entry point",          desc: "PyQt5 main window, menu bar, toolbar, and application lifecycle",                                type: "GUI"       },
  { file: "exam_form.py",         role: "Exam management dialog",           desc: "Qt dialog for creating and editing exams with title, description, and date fields",              type: "GUI"       },
  { file: "question_form.py",     role: "Question editor dialog",           desc: "Qt dialog for adding MCQ questions with 2-6 configurable choices and correct-answer selection",  type: "GUI"       },
  { file: "scanner.py",           role: "Main scanner module",              desc: "Orchestrates image preprocessing, bubble detection, and answer reading from scanned sheets",      type: "Scanner"   },
  { file: "circle_detector.py",   role: "Bubble detector v1",              desc: "First iteration using HoughCircles transform for bubble detection — limited accuracy",            type: "Scanner"   },
  { file: "circle_detection.py",  role: "Bubble detector v2",              desc: "Improved detector with contour filtering + area thresholding — better noise rejection",           type: "Scanner"   },
  { file: "robust_detection.py",  role: "Bubble detector v3 (final)",      desc: "Production-quality detector: contour area, circularity, and fill-ratio scoring in one pass",     type: "Scanner"   },
  { file: "generate_qcm_sheet.py",role: "Sheet generator",                  desc: "Generates HTML answer sheets via Jinja2 and converts to PDF using pdfkit/wkhtmltopdf",          type: "Generator" },
  { file: "database.py",          role: "Raw SQLite layer",                  desc: "Direct sqlite3 connection management with hand-written SQL queries — no ORM",                    type: "Database"  },
  { file: "qcm_template.html",    role: "Answer sheet Jinja2 template",     desc: "HTML template for printable A4 QCM answer sheets with bubble grid layout",                       type: "Template"  },
];

const TYPE_COLORS = {
  GUI:       "bg-indigo-500/10 text-indigo-500",
  Scanner:   "bg-cyan-500/10   text-cyan-500",
  Generator: "bg-amber-500/10  text-amber-500",
  Database:  "bg-emerald-500/10 text-emerald-500",
  Template:  "bg-pink-500/10   text-pink-500",
};

const COMPARISON = [
  {
    layer: "UI",
    old: { label: "PyQt5 Desktop",  detail: "QMainWindow, QDialog, QTableWidget widgets",      icon: Monitor, color: "text-slate-400"  },
    new: { label: "React 19 SPA",   detail: "Glassmorphism UI, TanStack Query, Recharts",       icon: Globe,   color: "text-cyan-500"   },
  },
  {
    layer: "Database",
    old: { label: "Raw SQLite",      detail: "sqlite3 module, hand-written SQL, no migrations",  icon: Database, color: "text-slate-400" },
    new: { label: "SQLAlchemy 2.0",  detail: "ORM models, Flask-Migrate, relationship mapping",  icon: Database, color: "text-emerald-500"},
  },
  {
    layer: "Scanner",
    old: { label: "6 Algorithm Iterations", detail: "HoughCircles → contours → robust_detection final", icon: ScanLine, color: "text-slate-400" },
    new: { label: "Clean Pipeline",          detail: "5 focused modules with debug output + config",      icon: ScanLine, color: "text-orange-500" },
  },
  {
    layer: "AI",
    old: { label: "None",              detail: "No AI component in original app",         icon: Brain, color: "text-slate-400"  },
    new: { label: "Qwen2.5-VL-3B",    detail: "OCR + evaluation + RAG feedback loop",    icon: Brain, color: "text-pink-500"   },
  },
];

const MILESTONES = [
  {
    version: "v0.1.0", label: "Desktop App", date: "Year 3 PFE",
    color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/30", dot: "bg-slate-500",
    desc: "Original PyQt5 desktop application with raw SQLite, basic scanner, and HTML/PDF sheet generation.",
    features: ["PyQt5 GUI", "Raw SQLite", "HoughCircles scanner", "pdfkit sheets"],
  },
  {
    version: "v0.2.0", label: "Web Restructuring", date: "Sub-Project 1–2",
    color: "text-indigo-500", bg: "bg-indigo-500/10", border: "border-indigo-500/30", dot: "bg-indigo-500",
    desc: "Complete rewrite: Flask REST API + React SPA. Layered architecture, SQLAlchemy ORM, improved scanner.",
    features: ["Flask API", "React + Vite", "SQLAlchemy ORM", "Clean scanner pipeline"],
  },
  {
    version: "v0.3.0", label: "AI Integration (Current)", date: "Sub-Project 3–4",
    color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30", dot: "bg-emerald-500",
    desc: "Qwen2.5-VL-3B-Instruct integrated for handwritten OCR, automated scoring, and RAG correction loop.",
    features: ["Qwen2.5-VL OCR", "RAG feedback", "4-bit quantisation", "Full thesis docs"],
  },
];

function FileTable() {
  const [filter, setFilter] = useState("All");
  const types = ["All", "GUI", "Scanner", "Generator", "Database", "Template"];
  const filtered = filter === "All" ? LEGACY_FILES : LEGACY_FILES.filter((f) => f.type === filter);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {types.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`text-xs px-3 py-1.5 rounded-full border cursor-pointer transition-all duration-200 font-medium ${
              filter === t
                ? "bg-primary text-primary-foreground border-primary"
                : "border-white/10 hover:bg-white/10 text-muted-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-white/10 bg-black/20">
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">File</th>
              <th className="px-4 py-3 text-left font-medium hidden sm:table-cell text-muted-foreground">Type</th>
              <th className="px-4 py-3 text-left font-medium hidden md:table-cell text-muted-foreground">Role</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Description</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="px-4 py-3">
                  <code className="font-mono text-primary">{row.file}</code>
                </td>
                <td className="px-4 py-3 hidden sm:table-cell">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${TYPE_COLORS[row.type]}`}>{row.type}</span>
                </td>
                <td className="px-4 py-3 hidden md:table-cell text-foreground">
                  {row.role}
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {row.desc}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function LegacyCode() {
  const [archExpanded, setArchExpanded] = useState(true);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Legacy Application"
        description="Archived PyQt5 desktop app — the original SmartGrader v0.1.0 preserved for reference."
        helpText="The legacy/ directory contains the original SmartGrader desktop application built with PyQt5. It is preserved for reference and comparison with the current web architecture."
      />

      {/* Overview */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-start gap-4">
          <div className="rounded-xl p-3 bg-slate-500/10 shrink-0">
            <Archive className="h-6 w-6 text-slate-400" />
          </div>
          <div>
            <h3 className="font-heading font-semibold text-lg mb-1 text-foreground">
              SmartGrader v0.1.0 — Desktop Application
            </h3>
            <p className="text-sm leading-relaxed text-muted-foreground">
              SmartGrader was originally developed as a PyQt5 desktop application as part of the initial PFE prototype.
              The legacy code is preserved in the <code className="font-mono bg-black/20 px-1 rounded text-xs">legacy/</code> directory
              for reference. It demonstrates the evolution of the scanner algorithm through 6 iterations and the original
              raw-SQLite database approach before the migration to SQLAlchemy ORM.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {["PyQt5 GUI", "Raw sqlite3", "6 scanner iterations", "pdfkit PDF generation", "No REST API", "Desktop only"].map((tag) => (
            <span key={tag} className="text-xs px-2.5 py-1 rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Architecture Comparison */}
      <div className="glass rounded-xl overflow-hidden">
        <button
          className="w-full flex items-center gap-3 px-6 py-4 cursor-pointer hover:bg-white/5 transition-all duration-200"
          onClick={() => setArchExpanded((v) => !v)}
        >
          <Layers className="h-5 w-5 text-primary" />
          <span className="font-heading font-semibold text-base flex-1 text-left text-foreground">
            Architecture Comparison: Old vs New
          </span>
          {archExpanded ? <ChevronDown className="h-4 w-4 opacity-40" /> : <ChevronRight className="h-4 w-4 opacity-40" />}
        </button>
        {archExpanded && (
          <div className="px-6 pb-6 space-y-3">
            <div className="grid grid-cols-3 gap-3 text-xs font-medium mb-1">
              <span className="text-muted-foreground">Layer</span>
              <span className="text-slate-400">Legacy (v0.1)</span>
              <span className="text-emerald-500">Current (v0.3)</span>
            </div>
            {COMPARISON.map((row, i) => {
              const OldIcon = row.old.icon;
              const NewIcon = row.new.icon;
              return (
                <div key={i} className="grid grid-cols-3 gap-3 p-3 rounded-xl bg-black/10 border border-white/5">
                  <div className="flex items-center">
                    <span className="text-xs font-medium text-foreground">{row.layer}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <OldIcon className={`h-3.5 w-3.5 shrink-0 mt-0.5 ${row.old.color}`} />
                    <div>
                      <p className={`text-xs font-medium ${row.old.color}`}>{row.old.label}</p>
                      <p className="text-xs opacity-60 text-muted-foreground">{row.old.detail}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <NewIcon className={`h-3.5 w-3.5 shrink-0 mt-0.5 ${row.new.color}`} />
                    <div>
                      <p className={`text-xs font-medium ${row.new.color}`}>{row.new.label}</p>
                      <p className="text-xs opacity-60 text-muted-foreground">{row.new.detail}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* File Inventory */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <FileCode className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">
            File Inventory <span className="text-sm font-normal opacity-60">legacy/</span>
          </h3>
        </div>
        <FileTable />
      </div>

      {/* How to Run Legacy */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Terminal className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">How to Run the Legacy App</h3>
        </div>
        <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/20 flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
          <p className="text-xs text-muted-foreground">
            The legacy app is for reference only. For active use, run the current Flask + React application instead.
          </p>
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-xs font-medium mb-1 text-muted-foreground">1. Install dependencies</p>
            <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-cyan-400">{`cd legacy/
pip install PyQt5 opencv-python pdfkit`}</pre>
          </div>
          <div>
            <p className="text-xs font-medium mb-1 text-muted-foreground">2. Install wkhtmltopdf (for PDF generation)</p>
            <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-emerald-400">{`# Windows: download from https://wkhtmltopdf.org/downloads.html
# Ubuntu:   sudo apt-get install wkhtmltopdf
# macOS:    brew install wkhtmltopdf`}</pre>
          </div>
          <div>
            <p className="text-xs font-medium mb-1 text-muted-foreground">3. Run the desktop app</p>
            <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-pink-400">{`python main.py`}</pre>
          </div>
        </div>
      </div>

      {/* Migration Timeline */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Clock className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Migration Timeline</h3>
        </div>
        <div className="space-y-0">
          {MILESTONES.map((m, i) => (
            <div key={i} className="flex gap-4">
              {/* Timeline line + dot */}
              <div className="flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full mt-1 shrink-0 ${m.dot}`} />
                {i < MILESTONES.length - 1 && (
                  <div className="w-px flex-1 my-1 bg-white/10" />
                )}
              </div>
              {/* Content */}
              <div className={`pb-6 flex-1 ${i === MILESTONES.length - 1 ? "pb-0" : ""}`}>
                <div className={`rounded-xl p-4 border ${m.border} ${m.bg}`}>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className={`font-mono font-bold text-sm ${m.color}`}>{m.version}</span>
                    <span className="font-heading font-semibold text-sm text-foreground">{m.label}</span>
                    <span className="text-xs opacity-50">{m.date}</span>
                    {i === MILESTONES.length - 1 && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 font-medium flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" /> Current
                      </span>
                    )}
                  </div>
                  <p className="text-xs mb-2 text-muted-foreground">{m.desc}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {m.features.map((f) => (
                      <span key={f} className={`text-xs px-2 py-0.5 rounded-full border border-current/20 ${m.color} ${m.bg}`}>{f}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
