import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/ui/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  BookOpen, CheckCircle2, Clock, GitBranch, FileText, Layers,
  Users, Activity, BarChart2, Lightbulb, ChevronDown, ChevronRight,
  Terminal, Download, ExternalLink, BookMarked, Network,
} from "lucide-react";
import { MarkdownPreviewModal } from "@/components/ui/markdown-preview-modal";
import { PumlPreviewModal } from "@/components/ui/puml-preview-modal";

const SUB_PROJECTS = [
  {
    id: "SP1", label: "Auth + Admin",
    desc: "JWT authentication, teacher/student login, barcode scan, admin panel, CSV student import. 4 new models, 15 endpoints.",
    color: "text-indigo-500", bg: "bg-indigo-500/10", border: "border-indigo-500/30",
    completed: true,
  },
  {
    id: "SP2", label: "Online Exam Engine",
    desc: "Student groups, exam sessions with configurable timer, take-exam UI with auto-save, live teacher monitoring dashboard.",
    color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30",
    completed: true,
  },
  {
    id: "SP3", label: "Anti-Cheat & Proctoring",
    desc: "BlazeFace face detection, tab/window event tracking, webcam snapshots, browser lockdown, teacher proctoring dashboard.",
    color: "text-pink-500", bg: "bg-pink-500/10", border: "border-pink-500/30",
    completed: true,
  },
  {
    id: "SP4", label: "LAN Mode + Deployment",
    desc: "University LAN server mode (--lan flag), Docker compose deployment, 191 automated tests, v1.0.0 release.",
    color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30",
    completed: true,
  },
];

const CHAPTERS = [
  {
    num: "01", title: "General Introduction",
    pages: "~18", status: "Complete",
    file: "01-introduction.md",
    topics: ["Problem Statement", "Objectives", "Methodology", "Project Scope", "4 Sub-Projects", "Document Structure"],
    summary: "Introduces the motivation for SmartGrader: the manual exam-grading bottleneck in Algerian universities. Defines the four sub-project roadmap (Auth/Admin, Online Exam Engine, Anti-Cheat Proctoring, LAN Deployment) and positions the work within the PFE framework.",
  },
  {
    num: "02", title: "State of the Art",
    pages: "~28", status: "Complete",
    file: "02-state-of-art.md",
    topics: ["OMR Systems", "OCR Technology", "Vision-Language Models", "LLaVA / Qwen2-VL", "RAG", "Online Exam Platforms", "Anti-Cheat Systems"],
    summary: "Surveys optical mark recognition (OMR) systems, modern OCR approaches, and vision-language models. Compares LLaVA, Qwen2-VL, and GPT-4V. Reviews online exam proctoring solutions and anti-cheat techniques used in academic platforms.",
  },
  {
    num: "03", title: "Analysis & Design",
    pages: "~38", status: "Complete",
    file: "03-analysis-design.md",
    topics: ["Requirements", "Use-Case Diagrams", "Auth Flow", "Exam Session Flow", "Class Diagram", "Sequence Diagrams", "ER Diagram", "Deployment"],
    summary: "Captures functional and non-functional requirements for all four phases. Presents 9 UML diagrams including authentication flow, online exam sequence, proctoring interaction, class diagram with ~15 models, ER diagram with full schema, and Docker deployment diagram.",
  },
  {
    num: "04", title: "Implementation",
    pages: "~45", status: "Complete",
    file: "04-implementation.md",
    topics: ["JWT Auth", "Admin Panel", "Student Groups", "Exam Sessions", "Timer Engine", "Anti-Cheat", "BlazeFace", "Scanner Pipeline", "AI Integration", "Docker"],
    summary: "Details the technical implementation of all four sub-projects. Covers JWT auth with PyJWT, exam session engine with auto-save and auto-submit, TensorFlow.js BlazeFace proctoring, the OpenCV bubble-detection pipeline, Qwen2.5-VL OCR integration, and Docker/LAN deployment.",
  },
  {
    num: "05", title: "Testing & Results",
    pages: "~25", status: "Complete",
    file: "05-testing-results.md",
    topics: ["191 pytest Tests", "Scanner Accuracy 96%", "Auth Tests", "Session Tests", "Proctor Tests", "AI Grading", "Performance Benchmarks", "User Acceptance"],
    summary: "Reports 191 automated tests covering models, services, scanner, auth, sessions, and proctoring routes. Documents 96% bubble detection accuracy on 50 test sheets. Presents session engine reliability metrics, anti-cheat detection rates, and API response-time benchmarks.",
  },
  {
    num: "06", title: "Conclusion",
    pages: "~12", status: "Complete",
    file: "06-conclusion.md",
    topics: ["Achievements", "v1.0.0 Release", "Limitations", "Future Work", "LMS Integration", "RAG Improvements"],
    summary: "Summarises achievements across all four sub-projects at v1.0.0. Identifies current limitations (GPU requirement, limited language support). Proposes future directions: multilingual OCR, batch scanning, LMS integration, and improved proctoring with liveness detection.",
  },
  {
    num: "A", title: "Appendices",
    pages: "~15", status: "Complete",
    file: "07-appendices.md",
    topics: ["Full API Spec (40+ endpoints)", "DB Schema (15 tables)", "Config Reference", "Docker Compose", "Sample Sheets", "BibTeX References"],
    summary: "Provides the complete API specification for all 40+ endpoints, database schema DDL for 15 tables, Docker compose configuration, configuration reference table, sample answer sheet images, and the full BibTeX bibliography.",
  },
];

const UML_DIAGRAMS = [
  { name: "System Use-Case",         type: "Use Case",   file: "use-case.puml",          desc: "Teacher, student, and admin actors with all system use cases including auth and proctoring", color: "text-indigo-500",  bg: "bg-indigo-500/10"  },
  { name: "Domain Class Diagram",    type: "Class",      file: "class-diagram.puml",     desc: "~15 ORM models: Exam, Question, Choice, Student, Group, Session, Attempt, ProctorEvent", color: "text-violet-500",  bg: "bg-violet-500/10"  },
  { name: "Auth Flow",               type: "Sequence",   file: "sequence-auth.puml",     desc: "Teacher login and student barcode-scan login → JWT issuance and refresh flow",          color: "text-yellow-500",  bg: "bg-yellow-500/10"  },
  { name: "Online Exam Flow",        type: "Sequence",   file: "sequence-exam.puml",     desc: "Session start → question delivery → auto-save answer → timer expire → auto-submit",     color: "text-cyan-500",    bg: "bg-cyan-500/10"    },
  { name: "Scan & Grade Flow",       type: "Sequence",   file: "sequence-scan.puml",     desc: "Upload → Preprocess → Detect → Grade → Save sequence",                                  color: "text-emerald-500", bg: "bg-emerald-500/10" },
  { name: "AI Grading Flow",         type: "Sequence",   file: "sequence-ai-grade.puml", desc: "Image → OCR → Evaluate → RAG correction pipeline",                                      color: "text-pink-500",    bg: "bg-pink-500/10"    },
  { name: "Entity-Relationship",     type: "ER Diagram", file: "er-diagram.puml",        desc: "Full database schema: 15 tables, foreign keys, and cardinalities",                       color: "text-amber-500",   bg: "bg-amber-500/10"   },
  { name: "Deployment Architecture", type: "Deployment", file: "deployment.puml",        desc: "Docker compose topology: Flask API, React SPA, GPU node, LAN server mode",               color: "text-teal-500",    bg: "bg-teal-500/10"    },
  { name: "Proctoring Interaction",  type: "Sequence",   file: "sequence-proctor.puml",  desc: "BlazeFace detection → event emit → snapshot upload → teacher dashboard update",         color: "text-orange-500",  bg: "bg-orange-500/10"  },
];

const KEY_REFS = [
  { key: "qwen2vl",  label: "Qwen2-VL",     desc: "Wang et al. (2024). Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution." },
  { key: "opencv",   label: "OpenCV",        desc: "Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools." },
  { key: "llava",    label: "LLaVA",         desc: "Liu et al. (2024). Visual Instruction Tuning. NeurIPS 2023." },
  { key: "rag",      label: "RAG",           desc: "Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS." },
  { key: "bitsb",    label: "BitsAndBytes",  desc: "Dettmers et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. NeurIPS." },
];

function ChapterCard({ chapter, onOpen }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="glass rounded-xl overflow-hidden">
      <button
        className="w-full flex items-start gap-4 p-5 hover:bg-white/5 transition-all duration-200 text-left cursor-pointer"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex flex-col items-center gap-1 shrink-0">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <span className="font-heading font-bold text-sm text-primary">
              {chapter.num === "A" ? "A" : chapter.num}
            </span>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="font-heading font-semibold text-sm text-foreground">
              Chapter {chapter.num !== "A" ? chapter.num : "Appendices"}: {chapter.title}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 font-medium">
              ✓ {chapter.status}
            </span>
            <span className="text-xs text-muted-foreground">{chapter.pages} pages</span>
          </div>
          <p className="text-xs leading-relaxed text-muted-foreground">{chapter.summary}</p>
          <div className="flex flex-wrap gap-1 mt-2">
            {chapter.topics.map((t) => (
              <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{t}</span>
            ))}
          </div>
        </div>
        {open ? <ChevronDown className="h-4 w-4 shrink-0 opacity-40 mt-1" /> : <ChevronRight className="h-4 w-4 shrink-0 opacity-40 mt-1" />}
      </button>
      {open && (
        <div className="border-t border-border px-5 py-3 bg-muted/30 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <FileText className="h-3.5 w-3.5" />
            <code className="font-mono">docs/thesis/{chapter.file}</code>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="cursor-pointer text-xs h-7"
            onClick={() => onOpen(chapter)}
          >
            <BookOpen className="h-3 w-3 mr-1" /> Read Chapter
          </Button>
        </div>
      )}
    </div>
  );
}

export default function AcademicDocs() {
  const navigate = useNavigate();
  const [mdModal, setMdModal] = useState({ open: false, filePath: "", title: "" });
  const [pumlModal, setPumlModal] = useState({ open: false, filename: "", title: "" });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Academic Thesis"
        description="PFE graduation project — full thesis documentation, UML diagrams, and build instructions."
        helpText="Browse all 6 thesis chapters, 9 UML diagrams, and the BibTeX bibliography for the SmartGrader v1.0.0 final-year project."
      />

      {/* Sub-project completion overview */}
      <div className="glass rounded-xl p-6 space-y-5">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h3 className="font-heading font-semibold text-lg text-foreground">
            Sub-Project Completion
          </h3>
          <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-600 font-semibold">
            4 / 4 Complete — 100%
          </span>
        </div>
        {/* Progress bar */}
        <div className="h-3 rounded-full bg-black/20 overflow-hidden flex">
          {SUB_PROJECTS.map((sp, i) => (
            <div key={sp.id} className={`flex-1 bg-emerald-500 ${i > 0 ? "border-l border-black/20" : ""} ${sp.completed ? "opacity-100" : "opacity-30"}`} />
          ))}
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {SUB_PROJECTS.map((sp) => (
            <div key={sp.id} className={`rounded-xl p-4 border ${sp.border} ${sp.bg}`}>
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className={`text-xs font-mono font-bold ${sp.color}`}>{sp.id}</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
              </div>
              <p className="font-heading font-semibold text-sm mb-1 text-foreground">{sp.label}</p>
              <p className="text-xs leading-relaxed text-muted-foreground">{sp.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Thesis Chapters */}
      <div className="space-y-4">
        <h3 className="font-heading font-semibold text-lg text-foreground">
          Thesis Chapters
        </h3>
        <div className="space-y-3">
          {CHAPTERS.map((ch) => (
            <ChapterCard
              key={ch.num}
              chapter={ch}
              onOpen={(ch) => setMdModal({ open: true, filePath: `docs/thesis/${ch.file}`, title: ch.title })}
            />
          ))}
        </div>
      </div>

      {/* UML Diagrams */}
      <div className="space-y-4">
        <h3 className="font-heading font-semibold text-lg text-foreground">
          UML Diagrams <span className="text-sm font-normal opacity-60">(9 PlantUML)</span>
        </h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {UML_DIAGRAMS.map((d, i) => (
            <div key={i} className="glass rounded-xl p-4 flex flex-col gap-3 hover:scale-[1.01] transition-all duration-200 cursor-pointer" onClick={() => setPumlModal({ open: true, filename: d.file, title: d.name })}>
              <div className={`flex items-center justify-center h-24 rounded-lg ${d.bg} border border-white/10`}>
                <Network className={`h-10 w-10 opacity-60 ${d.color}`} />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="font-heading font-semibold text-sm text-foreground">{d.name}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${d.bg} ${d.color}`}>{d.type}</span>
                <p className="text-xs mt-2 text-muted-foreground">{d.desc}</p>
              </div>
              <code className="text-xs font-mono opacity-50">{d.file}</code>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          PNG exports require running <code className="font-mono bg-black/20 px-1 rounded">plantuml *.puml</code> in <code className="font-mono bg-black/20 px-1 rounded">docs/figures/uml/</code>
        </p>
      </div>

      {/* Bibliography */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <BookMarked className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Bibliography</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">22 references</span>
        </div>
        <p className="text-sm text-muted-foreground">
          Complete bibliography in BibTeX format at <code className="font-mono bg-black/20 px-1 rounded text-xs">docs/thesis/bibliography.bib</code>. Key references:
        </p>
        <div className="space-y-2">
          {KEY_REFS.map((ref) => (
            <div key={ref.key} className="flex items-start gap-3 p-3 rounded-lg bg-black/10 border border-white/5">
              <code className="text-xs font-mono text-primary shrink-0 mt-0.5">@{ref.key}</code>
              <p className="text-xs leading-relaxed text-muted-foreground">{ref.desc}</p>
            </div>
          ))}
          <p className="text-xs italic text-muted-foreground">…and 17 more references covering Flask, PyJWT, TensorFlow.js, BlazeFace, Docker, React, TanStack Query, Pandoc, and Algerian education literature.</p>
        </div>
      </div>

      {/* Build Info */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Terminal className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Build the Thesis PDF</h3>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Python build script (recommended)</p>
            <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-emerald-400">{`python docs/thesis/build_pdf.py`}</pre>
            <p className="text-xs text-muted-foreground">Requires: markdown, xhtml2pdf, pyyaml</p>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Traditional Bash build</p>
            <pre className="text-xs font-mono p-3 rounded-lg bg-black/30 overflow-x-auto text-cyan-400">{`bash docs/thesis/build.sh`}</pre>
            <p className="text-xs text-muted-foreground">Requires: pandoc + XeLaTeX (TeX Live / MiKTeX)</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mt-2">
          <Button variant="outline" size="sm" className="cursor-pointer" onClick={() => window.open("/api/files/docs/thesis/thesis.pdf", "_blank")}>
            <Download className="h-3.5 w-3.5 mr-1.5" />
            Download Thesis PDF
          </Button>
          <Button variant="outline" size="sm" className="cursor-pointer" onClick={() => navigate("/documentation")}>
            <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
            Browse docs/ Folder
          </Button>
        </div>
      </div>

      <MarkdownPreviewModal
        open={mdModal.open}
        onClose={() => setMdModal({ open: false, filePath: "", title: "" })}
        filePath={mdModal.filePath}
        title={mdModal.title}
      />
      <PumlPreviewModal
        open={pumlModal.open}
        onClose={() => setPumlModal({ open: false, filename: "", title: "" })}
        filename={pumlModal.filename}
        title={pumlModal.title}
      />
    </div>
  );
}
