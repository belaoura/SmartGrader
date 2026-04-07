import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import {
  HelpCircle, BookOpen, ChevronDown, ChevronRight, Zap,
  FileText, ScanLine, Users, BarChart2, Brain, Settings,
  LayoutDashboard, CheckCircle2, AlertCircle, Keyboard,
  Info, MessageSquare, ArrowRight, Star, Code2, Globe,
} from "lucide-react";

const QUICK_STEPS = [
  {
    step: 1, icon: FileText,    color: "text-indigo-500", bg: "bg-indigo-500/10", border: "border-indigo-500/30",
    title: "Create an Exam",
    desc: "Go to the Exams page, click \"New Exam\", enter a title and description, then add your MCQ questions with 2–6 answer choices each.",
  },
  {
    step: 2, icon: ScanLine,   color: "text-cyan-500",   bg: "bg-cyan-500/10",   border: "border-cyan-500/30",
    title: "Generate & Print Answer Sheets",
    desc: "From the exam detail page, generate a printable A4 answer sheet. Print it and distribute to students during the exam.",
  },
  {
    step: 3, icon: CheckCircle2, color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/30",
    title: "Scan Completed Sheets",
    desc: "Go to the Scanner page, upload a photo or scan of the completed answer sheet, select the exam, and let SmartGrader detect the filled bubbles automatically.",
  },
  {
    step: 4, icon: BarChart2,  color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30",
    title: "View Results & Statistics",
    desc: "Check the Results page for individual student scores, pass/fail status, and the Dashboard for class-wide averages and charts.",
  },
];

const FEATURE_GUIDES = [
  {
    id: "dashboard", icon: LayoutDashboard, color: "text-indigo-500", title: "Dashboard",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>The Dashboard gives a bird's-eye view of your grading activity:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Stat cards:</strong> Total Exams, Total Questions, Total Students, Average Score</li>
          <li><strong className="text-foreground">Bar chart:</strong> Average score per exam — useful for comparing difficulty</li>
          <li><strong className="text-foreground">Pie chart:</strong> Pass / Fail distribution across all graded submissions</li>
        </ul>
        <p>Data updates in real-time as you create exams and scan answer sheets.</p>
      </div>
    ),
  },
  {
    id: "exams", icon: FileText, color: "text-violet-500", title: "Exams",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>Create and manage your exam library:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Create exam:</strong> Title + optional description</li>
          <li><strong className="text-foreground">Add questions:</strong> Up to 6 choices per question, mark exactly one as correct</li>
          <li><strong className="text-foreground">Edit / Delete:</strong> Manage questions from the exam detail page</li>
          <li><strong className="text-foreground">Answer sheet:</strong> Generate a printable HTML sheet with bubble grid</li>
        </ul>
        <p>Each exam tracks its own statistics (question count, average score, pass rate).</p>
      </div>
    ),
  },
  {
    id: "scanner", icon: ScanLine, color: "text-cyan-500", title: "Scanner",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>SmartGrader supports two scanning modes:</p>
        <div className="space-y-2">
          <div className="p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/20">
            <p className="font-medium text-cyan-600 text-xs mb-1">Mode 1 — MCQ Optical Scanning</p>
            <p>Upload a scanned JPG/PNG/PDF answer sheet. OpenCV detects filled bubbles and records student answers automatically. Achieves ~96% accuracy.</p>
          </div>
          <div className="p-3 rounded-lg bg-pink-500/5 border border-pink-500/20">
            <p className="font-medium text-pink-600 text-xs mb-1">Mode 2 — AI Short-Answer Grading</p>
            <p>For written answers, the Qwen2.5-VL-3B model first performs OCR to extract handwritten text, then evaluates it against the model answer or keywords.</p>
            <p className="mt-1 text-xs opacity-70">Requires a CUDA-compatible GPU with ~6–8 GB VRAM.</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "students", icon: Users, color: "text-orange-500", title: "Students",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>Manage your student roster:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Register student:</strong> Name, matricule (student ID), and email</li>
          <li><strong className="text-foreground">View profile:</strong> See all past exam results for a student</li>
          <li><strong className="text-foreground">Search & filter:</strong> Find students by name or matricule</li>
        </ul>
        <p>Students are matched to scan results automatically based on the matricule written on the answer sheet (AI OCR feature).</p>
      </div>
    ),
  },
  {
    id: "results", icon: BarChart2, color: "text-emerald-500", title: "Results",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>View and export grading results:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Per-exam table:</strong> Student name, score, percentage, Pass/Fail badge</li>
          <li><strong className="text-foreground">CSV export:</strong> Download all results as a spreadsheet</li>
          <li><strong className="text-foreground">Statistics:</strong> Average, highest, lowest score, pass rate</li>
        </ul>
        <p>Use <code className="font-mono bg-black/20 px-1 rounded text-xs">GET /api/results/exam/:id</code> to retrieve results via the API.</p>
      </div>
    ),
  },
  {
    id: "aiconfig", icon: Brain, color: "text-pink-500", title: "AI Configuration",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <p>The AI Configuration page shows all model and scanner settings from <code className="font-mono bg-black/20 px-1 rounded text-xs">app/config.py</code>:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Model status:</strong> Qwen2.5-VL-3B-Instruct with 4-bit NF4 quantisation</li>
          <li><strong className="text-foreground">Confidence threshold:</strong> 0.7 — grades below this are flagged for teacher review</li>
          <li><strong className="text-foreground">Scanner thresholds:</strong> Fill ratio, area min/max, circularity</li>
          <li><strong className="text-foreground">RAG loop:</strong> Teacher corrections improve future AI grading</li>
        </ul>
        <p>This page is currently read-only. Edit values directly in <code className="font-mono bg-black/20 px-1 rounded text-xs">app/config.py</code>.</p>
      </div>
    ),
  },
  {
    id: "settings", icon: Settings, color: "text-slate-400", title: "Settings",
    content: (
      <div className="space-y-2 text-sm text-muted-foreground">
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li><strong className="text-foreground">Dark mode toggle:</strong> Switch between light and dark glassmorphism theme</li>
          <li><strong className="text-foreground">App info:</strong> Version, build date, tech stack summary</li>
          <li><strong className="text-foreground">Database:</strong> SQLite connection status and path</li>
        </ul>
      </div>
    ),
  },
];

const FAQ = [
  {
    q: "What image formats are supported for scanning?",
    a: "The scanner accepts JPG/JPEG, PNG, and PDF files. PDF files are converted to images internally using pdf2image before processing. Multi-page PDFs process the first page only (one sheet per upload).",
    icon: ScanLine,
  },
  {
    q: "How accurate is the MCQ optical scanner?",
    a: "The contour-based bubble detector achieves approximately 96% accuracy on well-scanned A4 sheets with good contrast. Accuracy drops on low-quality scans (below 300 DPI), heavy shadows, or partial fill. Use the debug_output/ images to diagnose detection issues.",
    icon: CheckCircle2,
  },
  {
    q: "What GPU is needed for AI short-answer grading?",
    a: "A CUDA-compatible NVIDIA GPU with at least 6–8 GB VRAM is recommended. Tested on RTX 3060 (8 GB) and RTX 4090 (24 GB). Without a GPU, the model falls back to CPU inference which is ~20-30x slower. MCQ optical scanning works without any GPU.",
    icon: Brain,
  },
  {
    q: "How does the RAG feedback loop improve grading?",
    a: "When a teacher corrects an AI-generated grade (via POST /api/ai/correct), the correction is stored in the ai_corrections table. On subsequent evaluations of similar questions, SmartGrader retrieves relevant past corrections and includes them as context for the AI model, progressively improving grading consistency.",
    icon: MessageSquare,
  },
  {
    q: "Can I export results to a spreadsheet?",
    a: "Yes. From the Results page, click the CSV Export button to download all results for the selected exam as a .csv file compatible with Excel and Google Sheets. The export includes student name, matricule, score, percentage, and pass/fail status.",
    icon: BarChart2,
  },
  {
    q: "How do I run SmartGrader locally?",
    a: "Install Python 3.10+ and Node.js 18+. Run: pip install -r requirements.txt && python run.py for the backend (http://localhost:5000), and cd frontend && npm install && npm run dev for the frontend (http://localhost:5173).",
    icon: Code2,
  },
];

const SHORTCUTS = [
  { keys: ["Ctrl", "K"], desc: "Open command palette (browser default)" },
  { keys: ["Tab"],       desc: "Navigate between form fields"            },
  { keys: ["Escape"],    desc: "Close dialogs and modals"                },
  { keys: ["Enter"],     desc: "Confirm dialogs and submit forms"        },
  { keys: ["F5"],        desc: "Reload page / refetch data"              },
];

function AccordionItem({ id, icon: Icon, color, title, content, activeId, setActiveId }) {
  const open = activeId === id;
  return (
    <div className="border border-white/10 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-5 py-4 cursor-pointer hover:bg-white/5 transition-all duration-200 text-left"
        onClick={() => setActiveId(open ? null : id)}
      >
        <Icon className={`h-5 w-5 shrink-0 ${color}`} />
        <span className="font-heading font-semibold text-sm flex-1 text-foreground">{title}</span>
        {open ? <ChevronDown className="h-4 w-4 opacity-40" /> : <ChevronRight className="h-4 w-4 opacity-40" />}
      </button>
      {open && (
        <div className="border-t border-white/10 px-5 py-4 bg-black/10">
          {content}
        </div>
      )}
    </div>
  );
}

function FaqItem({ item }) {
  const [open, setOpen] = useState(false);
  const Icon = item.icon;
  return (
    <div className="border border-white/10 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-start gap-3 px-5 py-4 cursor-pointer hover:bg-white/5 transition-all duration-200 text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <Icon className="h-4 w-4 text-primary shrink-0 mt-0.5" />
        <span className="text-sm flex-1 text-foreground">{item.q}</span>
        {open ? <ChevronDown className="h-4 w-4 opacity-40 shrink-0" /> : <ChevronRight className="h-4 w-4 opacity-40 shrink-0" />}
      </button>
      {open && (
        <div className="border-t border-white/10 px-5 py-4 bg-black/10">
          <p className="text-sm leading-relaxed text-muted-foreground">{item.a}</p>
        </div>
      )}
    </div>
  );
}

export default function Help() {
  const [activeFeature, setActiveFeature] = useState("dashboard");

  return (
    <div className="space-y-8">
      <PageHeader
        title="Help & User Guide"
        description="Step-by-step guides, feature documentation, FAQs, and usage tips."
        helpText="Everything you need to know about using SmartGrader — from creating your first exam to interpreting AI grading results."
      />

      {/* Quick Start */}
      <div className="glass rounded-xl p-6 space-y-5">
        <div className="flex items-center gap-3">
          <Zap className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Quick Start Guide</h3>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_STEPS.map((s, i) => {
            const Icon = s.icon;
            return (
              <div key={i} className={`rounded-xl p-4 border ${s.border} ${s.bg} flex flex-col gap-3`}>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold text-primary">{s.step}</span>
                  </div>
                  <Icon className={`h-4 w-4 ${s.color}`} />
                </div>
                <div>
                  <p className="font-heading font-semibold text-sm mb-1 text-foreground">{s.title}</p>
                  <p className="text-xs leading-relaxed text-muted-foreground">{s.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Guide */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <BookOpen className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Feature Guide</h3>
        </div>
        <div className="space-y-2">
          {FEATURE_GUIDES.map((f) => (
            <AccordionItem
              key={f.id}
              id={f.id}
              icon={f.icon}
              color={f.color}
              title={f.title}
              content={f.content}
              activeId={activeFeature}
              setActiveId={setActiveFeature}
            />
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <HelpCircle className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">
            Frequently Asked Questions
          </h3>
        </div>
        <div className="space-y-2">
          {FAQ.map((item, i) => (
            <FaqItem key={i} item={item} />
          ))}
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Keyboard className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">Keyboard Shortcuts</h3>
        </div>
        <p className="text-sm text-muted-foreground">
          SmartGrader uses standard browser keyboard shortcuts. Application-specific hotkeys are planned for a future release.
        </p>
        <div className="space-y-2">
          {SHORTCUTS.map((s, i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-black/10 border border-white/5">
              <div className="flex items-center gap-1 shrink-0">
                {s.keys.map((k) => (
                  <kbd
                    key={k}
                    className="inline-flex items-center justify-center px-2 py-0.5 rounded border border-white/20 bg-white/10 text-xs font-mono font-medium text-foreground"
                  >
                    {k}
                  </kbd>
                ))}
              </div>
              <span className="text-sm text-muted-foreground">{s.desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* About */}
      <div className="glass rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Info className="h-5 w-5 text-primary" />
          <h3 className="font-heading font-semibold text-lg text-foreground">About SmartGrader</h3>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Version</span>
              <span className="text-xs font-mono font-bold text-primary">v0.3.0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Type</span>
              <span className="text-xs">PFE Graduation Project</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Institution</span>
              <span className="text-xs">Algerian University</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Backend</span>
              <span className="text-xs font-mono">Python 3.10 · Flask 3.1</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Frontend</span>
              <span className="text-xs font-mono">React 19 · Vite 6 · Tailwind 4</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">AI Model</span>
              <span className="text-xs font-mono">Qwen2.5-VL-3B (4-bit NF4)</span>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-primary" />
              <span className="font-heading font-semibold text-sm text-foreground">Project Summary</span>
            </div>
            <p className="text-xs leading-relaxed text-muted-foreground">
              SmartGrader automates the exam-grading workflow for Algerian university instructors.
              It generates printable MCQ answer sheets, optically scans completed sheets using computer vision,
              and uses a vision-language AI model to grade handwritten short answers with a teacher-in-the-loop
              RAG correction feedback system.
            </p>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {["Flask API", "React SPA", "OpenCV", "Qwen2.5-VL", "RAG", "SQLAlchemy"].map((tag) => (
                <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{tag}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
