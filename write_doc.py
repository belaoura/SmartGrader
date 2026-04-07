#!/usr/bin/env python3
"""Script to write Documentation.jsx with all required changes."""

content = (
    "import { useState } from \"react\";\n"
    "import { MarkdownPreviewModal } from \"@/components/ui/markdown-preview-modal\";\n"
    "import { PageHeader } from \"@/components/ui/page-header\";\n"
    "import { Badge } from \"@/components/ui/badge\";\n"
    "import { Button } from \"@/components/ui/button\";\n"
    "import {\n"
    "  Code2, ChevronDown, ChevronRight, ExternalLink, Book, GitBranch,\n"
    "  Server, Database, Layers, ArrowRight, Zap, Globe, Shield,\n"
    "  FileText, Users, Brain, ScanLine, BarChart2, Activity,\n"
    "} from \"lucide-react\";\n"
    "\n"
    "const METHOD_STYLES = {\n"
    "  GET:    { bg: \"bg-emerald-500/15 text-emerald-600 dark:text-emerald-400\",  label: \"GET\"    },\n"
    "  POST:   { bg: \"bg-blue-500/15    text-blue-600    dark:text-blue-400\",     label: \"POST\"   },\n"
    "  PUT:    { bg: \"bg-amber-500/15   text-amber-600   dark:text-amber-400\",    label: \"PUT\"    },\n"
    "  DELETE: { bg: \"bg-red-500/15     text-red-600     dark:text-red-400\",      label: \"DELETE\" },\n"
    "};\n"
    "\n"
)

# Read the original file to get the large data blocks unchanged
with open("C:/Users/pc/Desktop/SmartGrader_APP_WithPDF/frontend/src/pages/Documentation.jsx", "r", encoding="utf-8") as f:
    original = f.read()

# Find ENDPOINT_GROUPS start and TECH_STACK end
eg_start = original.index("const ENDPOINT_GROUPS")
ts_end = original.index("\nfunction MethodBadge")

middle_section = original[eg_start:ts_end]

component_code = """
function MethodBadge({ method }) {
  const s = METHOD_STYLES[method] || METHOD_STYLES.GET;
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-mono font-bold ${s.bg}`}>
      {s.label}
    </span>
  );
}

function EndpointRow({ endpoint }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-white/10 rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-all duration-200 cursor-pointer text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <MethodBadge method={endpoint.method} />
        <code className="flex-1 text-sm font-mono text-foreground">
          {endpoint.path}
        </code>
        <span className="text-xs hidden sm:block text-muted-foreground">
          {endpoint.desc}
        </span>
        {open ? <ChevronDown className="h-4 w-4 shrink-0 opacity-50" /> : <ChevronRight className="h-4 w-4 shrink-0 opacity-50" />}
      </button>
      {open && (
        <div className="border-t border-white/10 px-4 py-3 bg-black/20">
          <p className="text-xs mb-2 sm:hidden text-muted-foreground">{endpoint.desc}</p>
          <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-muted-foreground">
            {endpoint.example}
          </pre>
        </div>
      )}
    </div>
  );
}

function EndpointGroup({ group }) {
  const [open, setOpen] = useState(true);
  const Icon = group.icon;
  return (
    <div className="glass rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-6 py-4 cursor-pointer hover:bg-white/5 transition-all duration-200"
        onClick={() => setOpen((v) => !v)}
      >
        <Icon className={`h-5 w-5 ${group.color}`} />
        <span className="font-heading font-semibold text-base flex-1 text-left text-foreground">
          {group.label}
        </span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-muted-foreground">
          {group.endpoints.length} endpoints
        </span>
        {open ? <ChevronDown className="h-4 w-4 opacity-50" /> : <ChevronRight className="h-4 w-4 opacity-50" />}
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-2">
          {group.endpoints.map((ep, i) => (
            <EndpointRow key={i} endpoint={ep} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Documentation() {
  const [activeTab, setActiveTab] = useState("api");
  const [mdModal, setMdModal] = useState({ open: false, filePath: "", title: "" });

  const tabs = [
    { id: "api",      label: "API Reference",   icon: Code2     },
    { id: "arch",     label: "Architecture",     icon: Layers    },
    { id: "stack",    label: "Tech Stack",       icon: Zap       },
    { id: "links",    label: "Quick Links",      icon: ExternalLink },
  ];

  const quickLinks = [
    {
      icon: FileText,
      label: "Thesis PDF",
      desc: "Complete academic PFE documentation (pandoc + XeLaTeX build)",
      color: "text-indigo-500",
      bg: "bg-indigo-500/10",
      action: "Open",
      onClick: () => window.open("/api/files/docs/thesis/thesis.pdf", "_blank"),
    },
    {
      icon: GitBranch,
      label: "GitHub Repository",
      desc: "Source code repository with full commit history and CI setup",
      color: "text-slate-500",
      bg: "bg-slate-500/10",
      action: "View",
      onClick: () => window.open("https://github.com/", "_blank"),
    },
    {
      icon: Book,
      label: "Installation Guide",
      desc: "Step-by-step guide: Python env, CUDA setup, npm install, run.py",
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
      action: "Open",
      onClick: () => setMdModal({ open: true, filePath: "docs/thesis/07-appendices.md", title: "Installation Guide" }),
    },
    {
      icon: Users,
      label: "User Manual",
      desc: "End-user manual for teachers: exams, scanning, results, export",
      color: "text-cyan-500",
      bg: "bg-cyan-500/10",
      action: "Open",
      onClick: () => setMdModal({ open: true, filePath: "docs/thesis/07-appendices.md", title: "User Manual" }),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="API Reference & Docs"
        description="Complete documentation for the SmartGrader REST API, architecture, and tech stack."
        helpText="Browse all 15+ API endpoints grouped by resource, explore the system architecture, and view the full technology stack."
      />

      {/* Tab bar */}
      <div className="glass rounded-xl p-1 flex gap-1 flex-wrap">
        {tabs.map((t) => {
          const Icon = t.icon;
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-all duration-200 ${
                active
                  ? "bg-primary text-primary-foreground shadow"
                  : "hover:bg-white/10 text-muted-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* API Reference */}
      {activeTab === "api" && (
        <div className="space-y-4">
          <div className="glass rounded-xl p-4 flex flex-wrap gap-3 items-center">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Base URL:</span>
              <code className="text-xs font-mono px-2 py-1 rounded bg-black/20 text-primary">http://localhost:5000</code>
            </div>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(METHOD_STYLES).map(([m, s]) => (
                <span key={m} className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-mono font-bold ${s.bg}`}>{s.label}</span>
              ))}
            </div>
          </div>
          {ENDPOINT_GROUPS.map((g) => (
            <EndpointGroup key={g.id} group={g} />
          ))}
        </div>
      )}

      {/* Architecture */}
      {activeTab === "arch" && (
        <div className="space-y-6">
          <div className="glass rounded-xl p-6 space-y-6">
            <h3 className="font-heading font-semibold text-lg text-foreground">
              3-Tier System Architecture
            </h3>
            {/* Flow diagram */}
            <div className="flex flex-col md:flex-row items-center justify-center gap-4">
              {[
                { icon: Globe,    label: "React Frontend",  sub: "Vite \u00b7 React 19 \u00b7 TanStack Query",   color: "border-cyan-500/30    bg-cyan-500/10",   text: "text-cyan-600"    },
                { icon: Server,   label: "Flask API",       sub: "Python 3.10 \u00b7 Flask 3.1 \u00b7 Blueprints", color: "border-indigo-500/30  bg-indigo-500/10", text: "text-indigo-500"  },
                { icon: Database, label: "SQLite + AI",     sub: "SQLAlchemy 2.0 \u00b7 Qwen2.5-VL-3B",     color: "border-emerald-500/30 bg-emerald-500/10", text: "text-emerald-600" },
              ].map((tier, i) => {
                const Icon = tier.icon;
                return (
                  <div key={i} className="flex items-center gap-4">
                    <div className={`flex flex-col items-center gap-2 border rounded-xl px-6 py-4 min-w-44 text-center ${tier.color}`}>
                      <Icon className={`h-8 w-8 ${tier.text}`} />
                      <span className="font-heading font-semibold text-sm text-foreground">{tier.label}</span>
                      <span className="text-xs text-muted-foreground">{tier.sub}</span>
                    </div>
                    {i < 2 && <ArrowRight className="h-6 w-6 shrink-0 hidden md:block opacity-40" />}
                    {i < 2 && <ArrowRight className="h-6 w-6 shrink-0 md:hidden rotate-90 opacity-40" />}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "Layered Design",     icon: Layers,  desc: "Routes \u2192 Services \u2192 Models. Each layer has a single responsibility. Routes are thin HTTP handlers; all business logic lives in services." },
              { title: "Pure Scanner Modules", icon: ScanLine, desc: "Scanner modules (preprocessor, marker_finder, detector, grid_mapper, answer_reader) are pure image processing with zero DB dependencies." },
              { title: "Custom Exceptions",  icon: Shield,  desc: "app/errors.py defines ScannerError, GradingError, NotFoundError with HTTP status codes for consistent JSON error responses." },
            ].map((c, i) => {
              const Icon = c.icon;
              return (
                <div key={i} className="glass rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <Icon className="h-5 w-5 text-primary" />
                    <h4 className="font-heading font-semibold text-sm text-foreground">{c.title}</h4>
                  </div>
                  <p className="text-xs leading-relaxed text-muted-foreground">{c.desc}</p>
                </div>
              );
            })}
          </div>

          {/* Directory tree */}
          <div className="glass rounded-xl p-6">
            <h3 className="font-heading font-semibold mb-4" style={{ color: "var(--color-foreground)" }}>Directory Structure</h3>
            <pre className="text-xs font-mono leading-relaxed overflow-x-auto" style={{ color: "var(--color-muted-foreground)" }}>{`app/
  __init__.py          # Flask app factory (create_app)
  config.py            # All configuration values
  errors.py            # Custom exceptions with HTTP codes
  models/              # SQLAlchemy ORM (Exam, Student, Result)
  services/            # Business logic layer
    exam_service.py
    grading_service.py
    scanner_service.py
  scanner/             # Pure image processing
    preprocessor.py    \u2192 Deskew, crop, grayscale, threshold
    marker_finder.py   \u2192 Triangle alignment marker detection
    detector.py        \u2192 Contour-based bubble detection
    grid_mapper.py     \u2192 Map bubbles to question/choice grid
    answer_reader.py   \u2192 Read filled answers from grid
  routes/              # Flask blueprints (thin HTTP layer)
  ai/                  # Qwen2.5-VL integration (Sub-Project 3)
frontend/              # React + Vite SPA`}</pre>
          </div>
        </div>
      )}

      {/* Tech Stack */}
      {activeTab === "stack" && (
        <div className="space-y-4">
          <div className="glass rounded-xl p-6">
            <h3 className="font-heading font-semibold text-lg mb-4" style={{ color: "var(--color-foreground)" }}>Full Technology Stack</h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {TECH_STACK.map((tech, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-white/10 hover:bg-white/5 transition-all duration-200">
                  <div className={`rounded-lg p-2 shrink-0 ${tech.color.split(" ")[0]}`}>
                    <Zap className={`h-4 w-4 ${tech.color.split(" ")[1]}`} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm" style={{ color: "var(--color-foreground)" }}>{tech.name}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded bg-white/10 font-mono" style={{ color: "var(--color-muted-foreground)" }}>v{tech.version}</span>
                    </div>
                    <p className="text-xs mt-0.5" style={{ color: "var(--color-muted-foreground)" }}>{tech.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quick Links */}
      {activeTab === "links" && (
        <div className="grid gap-4 sm:grid-cols-2">
          {quickLinks.map((link, i) => {
            const Icon = link.icon;
            return (
              <div key={i} className="glass rounded-xl p-6 flex flex-col gap-4 hover:scale-[1.01] transition-all duration-200">
                <div className="flex items-start gap-4">
                  <div className={`rounded-xl p-3 ${link.bg}`}>
                    <Icon className={`h-6 w-6 ${link.color}`} />
                  </div>
                  <div>
                    <h4 className="font-heading font-semibold" style={{ color: "var(--color-foreground)" }}>{link.label}</h4>
                    <p className="text-xs mt-1 leading-relaxed" style={{ color: "var(--color-muted-foreground)" }}>{link.desc}</p>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="self-start cursor-pointer" onClick={link.onClick}>
                  <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                  {link.action}
                </Button>
              </div>
            );
          })}
        </div>
      )}

      <MarkdownPreviewModal
        open={mdModal.open}
        onClose={() => setMdModal({ open: false, filePath: "", title: "" })}
        filePath={mdModal.filePath}
        title={mdModal.title}
      />
    </div>
  );
}
"""

# Build imports + data section + component
imports = """import { useState } from "react";
import { MarkdownPreviewModal } from "@/components/ui/markdown-preview-modal";
import { PageHeader } from "@/components/ui/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Code2, ChevronDown, ChevronRight, ExternalLink, Book, GitBranch,
  Server, Database, Layers, ArrowRight, Zap, Globe, Shield,
  FileText, Users, Brain, ScanLine, BarChart2, Activity,
} from "lucide-react";

"""

with open("C:/Users/pc/Desktop/SmartGrader_APP_WithPDF/frontend/src/pages/Documentation.jsx", "r", encoding="utf-8") as f:
    original = f.read()

# Find ENDPOINT_GROUPS start and end of TECH_STACK (just before function MethodBadge)
eg_start = original.index("const ENDPOINT_GROUPS")
ts_end = original.index("\nfunction MethodBadge")
data_section = original[eg_start:ts_end]

final_content = imports + data_section + "\n" + component_code

with open("C:/Users/pc/Desktop/SmartGrader_APP_WithPDF/frontend/src/pages/Documentation.jsx", "w", encoding="utf-8") as f:
    f.write(final_content)

print("Done! Lines written:", len(final_content.splitlines()))
