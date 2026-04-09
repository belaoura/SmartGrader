import { useState } from "react";
import { MarkdownPreviewModal } from "@/components/ui/markdown-preview-modal";
import { PageHeader } from "@/components/ui/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Code2, ChevronDown, ChevronRight, ExternalLink, Book, GitBranch,
  Server, Database, Layers, ArrowRight, Zap, Globe, Shield,
  FileText, Users, Brain, ScanLine, BarChart2, Activity,
  Lock, UserCheck, MonitorPlay, Eye, GraduationCap,
} from "lucide-react";

const ENDPOINT_GROUPS = [
  {
    id: "auth",
    label: "Authentication",
    icon: Lock,
    color: "text-yellow-500",
    endpoints: [
      { method: "POST", path: "/api/auth/login",   desc: "Teacher login with email + password, returns JWT",
        example: `// Request body\n{ "email": "teacher@univ.dz", "password": "secret" }\n\n// Response 200\n{ "access_token": "eyJ...", "refresh_token": "eyJ...", "user": { "id": 1, "role": "teacher" } }` },
      { method: "POST", path: "/api/auth/scan",    desc: "Student login by scanning barcode/QR on student card",
        example: `// Request body\n{ "barcode": "20210001" }\n\n// Response 200\n{ "access_token": "eyJ...", "student": { "id": 5, "name": "Amina Benali" } }` },
      { method: "POST", path: "/api/auth/refresh", desc: "Refresh expired access token using refresh token",
        example: `// Request body\n{ "refresh_token": "eyJ..." }\n\n// Response 200\n{ "access_token": "eyJ..." }` },
      { method: "POST", path: "/api/auth/logout",  desc: "Invalidate current session and blacklist the token",
        example: `// Header: Authorization: Bearer <token>\n// Response: 204 No Content` },
      { method: "GET",  path: "/api/auth/me",      desc: "Get the currently authenticated user profile",
        example: `// Response 200\n{ "id": 1, "email": "teacher@univ.dz", "role": "teacher", "name": "Dr. Benali" }` },
    ],
  },
  {
    id: "admin",
    label: "Admin",
    icon: UserCheck,
    color: "text-rose-500",
    endpoints: [
      { method: "POST",   path: "/api/admin/teachers",            desc: "Create a new teacher account (admin only)",
        example: `// Request body\n{ "name": "Dr. Khelifi", "email": "khelifi@univ.dz", "password": "secure123" }\n// Response: 201 Created` },
      { method: "GET",    path: "/api/admin/teachers",            desc: "List all teacher accounts",
        example: `[\n  { "id": 1, "name": "Dr. Khelifi", "email": "khelifi@univ.dz", "created_at": "..." }\n]` },
      { method: "DELETE", path: "/api/admin/teachers/:id",        desc: "Remove a teacher account by ID",
        example: `// Response: 204 No Content` },
      { method: "POST",   path: "/api/admin/students/import",     desc: "Bulk import students from CSV file",
        example: `// Multipart: file (.csv) with columns: name, matricule, email\n// Response 201\n{ "imported": 45, "skipped": 2, "errors": [] }` },
    ],
  },
  {
    id: "groups",
    label: "Student Groups",
    icon: Users,
    color: "text-cyan-500",
    endpoints: [
      { method: "POST",   path: "/api/groups",                    desc: "Create a new student group",
        example: `// Request body\n{ "name": "L3 InfoA 2024", "description": "Licence 3 section A" }\n// Response: 201 Created\n{ "id": 3, "name": "L3 InfoA 2024", "member_count": 0 }` },
      { method: "GET",    path: "/api/groups",                    desc: "List all groups with member counts",
        example: `[\n  { "id": 3, "name": "L3 InfoA 2024", "member_count": 32 }\n]` },
      { method: "GET",    path: "/api/groups/:id",                desc: "Get group details with full member list",
        example: `{ "id": 3, "name": "L3 InfoA 2024", "members": [{ "id": 1, "name": "Amina Benali" }] }` },
      { method: "DELETE", path: "/api/groups/:id",                desc: "Delete a group (members are not deleted)",
        example: `// Response: 204 No Content` },
      { method: "POST",   path: "/api/groups/:id/members",        desc: "Add students to a group by student IDs",
        example: `// Request body\n{ "student_ids": [1, 2, 5, 12] }\n// Response 200\n{ "added": 4 }` },
      { method: "DELETE", path: "/api/groups/:id/members/:sid",   desc: "Remove one student from a group",
        example: `// Response: 204 No Content` },
    ],
  },
  {
    id: "sessions",
    label: "Exam Sessions",
    icon: MonitorPlay,
    color: "text-violet-500",
    endpoints: [
      { method: "POST",   path: "/api/sessions",                  desc: "Create a new online exam session",
        example: `// Request body\n{ "exam_id": 1, "group_id": 3, "duration_minutes": 60, "start_at": "2024-06-01T09:00:00Z", "proctoring": true }\n// Response: 201 Created` },
      { method: "GET",    path: "/api/sessions",                  desc: "List all sessions (teacher sees own, student sees assigned)",
        example: `[\n  { "id": 10, "exam_title": "Math Quiz", "status": "scheduled", "duration_minutes": 60 }\n]` },
      { method: "GET",    path: "/api/sessions/:id",              desc: "Get full session details and current status",
        example: `{ "id": 10, "exam_id": 1, "group_id": 3, "status": "active", "started_at": "...", "submissions": 12 }` },
      { method: "PUT",    path: "/api/sessions/:id",              desc: "Update session settings (before start only)",
        example: `// Request body\n{ "duration_minutes": 90, "proctoring": false }` },
      { method: "DELETE", path: "/api/sessions/:id",              desc: "Cancel and delete a session",
        example: `// Response: 204 No Content` },
      { method: "POST",   path: "/api/sessions/:id/assign",       desc: "Assign additional students to a session",
        example: `// Request body\n{ "student_ids": [7, 8] }\n// Response 200\n{ "assigned": 2 }` },
      { method: "GET",    path: "/api/sessions/:id/monitor",      desc: "Live monitoring data for a running session",
        example: `{ "active_students": 28, "submitted": 5, "flagged": 2, "time_remaining_seconds": 1820 }` },
    ],
  },
  {
    id: "student_exam",
    label: "Student Exam",
    icon: GraduationCap,
    color: "text-emerald-500",
    endpoints: [
      { method: "GET",  path: "/api/student/exams",               desc: "List all exams assigned to the logged-in student",
        example: `[\n  { "session_id": 10, "exam_title": "Math Quiz", "status": "assigned", "starts_at": "..." }\n]` },
      { method: "POST", path: "/api/student/exams/:id/start",     desc: "Start a session — initialises timer and locks browser",
        example: `// Response 200\n{ "questions": [...], "duration_seconds": 3600, "session_token": "abc123" }` },
      { method: "GET",  path: "/api/student/exams/:id/status",    desc: "Get current exam status and remaining time",
        example: `{ "status": "in_progress", "time_remaining_seconds": 2400, "answered": 8, "total": 20 }` },
      { method: "POST", path: "/api/student/exams/:id/answer",    desc: "Save a single answer (auto-save on selection)",
        example: `// Request body\n{ "question_id": 5, "choice_id": 18 }\n// Response 200\n{ "saved": true }` },
      { method: "POST", path: "/api/student/exams/:id/answers",   desc: "Bulk save multiple answers at once",
        example: `// Request body\n{ "answers": [{ "question_id": 1, "choice_id": 3 }, ...] }\n// Response 200\n{ "saved": 20 }` },
      { method: "POST", path: "/api/student/exams/:id/submit",    desc: "Final submission — ends exam, triggers grading",
        example: `// Response 200\n{ "submitted_at": "...", "score": 16, "max_score": 20 }` },
      { method: "GET",  path: "/api/student/exams/:id/result",    desc: "View result after exam ends (if teacher released)",
        example: `{ "score": 16, "max_score": 20, "percentage": 80.0, "passed": true, "answers": { "1": "B", ... } }` },
    ],
  },
  {
    id: "proctor_student",
    label: "Proctoring (Student)",
    icon: Eye,
    color: "text-orange-500",
    endpoints: [
      { method: "POST", path: "/api/proctor/event",               desc: "Report a cheat-detection event from the client side",
        example: `// Request body\n{ "session_id": 10, "type": "tab_switch", "detail": "User switched to another tab", "timestamp": "..." }\n// Response: 204` },
      { method: "POST", path: "/api/proctor/snapshot",            desc: "Upload a webcam snapshot for proctoring review",
        example: `// Multipart: file (image/jpeg) + session_id\n// Response 200\n{ "snapshot_id": 42, "flagged": false }` },
      { method: "GET",  path: "/api/proctor/status",              desc: "Get proctoring config for the active session",
        example: `{ "webcam_required": true, "snapshot_interval_seconds": 30, "lockdown_mode": true }` },
    ],
  },
  {
    id: "proctor_teacher",
    label: "Proctoring (Teacher)",
    icon: Shield,
    color: "text-pink-500",
    endpoints: [
      { method: "GET",  path: "/api/proctor/events",              desc: "List all cheat events for a session (query ?session_id=)",
        example: `[\n  { "id": 1, "student": "Amina Benali", "type": "tab_switch", "timestamp": "...", "flagged": false }\n]` },
      { method: "GET",  path: "/api/proctor/snapshots",           desc: "List webcam snapshots for a session",
        example: `[\n  { "id": 42, "student_id": 5, "taken_at": "...", "flagged": false, "url": "/api/proctor/snapshots/42/image" }\n]` },
      { method: "GET",  path: "/api/proctor/summary",             desc: "Proctoring summary — event counts and risk scores per student",
        example: `[\n  { "student_id": 5, "name": "Amina", "events": 3, "snapshots": 6, "risk_score": 0.4 }\n]` },
      { method: "POST", path: "/api/proctor/capture/:sid",        desc: "Request an on-demand webcam snapshot from a student",
        example: `// Response 202 Accepted — snapshot will arrive via /api/proctor/snapshot` },
      { method: "POST", path: "/api/proctor/flag/:aid",           desc: "Manually flag or unflag an attempt for review",
        example: `// Request body\n{ "flagged": true, "reason": "Suspicious tab switching pattern" }` },
      { method: "GET",  path: "/api/proctor/snapshots/:id/image", desc: "Download the raw webcam snapshot image",
        example: `// Response: image/jpeg binary stream` },
    ],
  },
  {
    id: "exams",
    label: "Exams",
    icon: FileText,
    color: "text-indigo-500",
    endpoints: [
      { method: "GET",    path: "/api/exams",          desc: "List all exams with statistics",
        example: `// Response\n[\n  {\n    "id": 1,\n    "title": "Math Quiz",\n    "statistics": { "question_count": 20, "average_score": 78.5 }\n  }\n]` },
      { method: "POST",   path: "/api/exams",          desc: "Create a new exam",
        example: `// Request body\n{ "title": "Biology Midterm", "description": "Ch. 1-5" }\n\n// Response: 201 Created\n{ "id": 2, "title": "Biology Midterm", ... }` },
      { method: "GET",    path: "/api/exams/:id",      desc: "Retrieve a single exam by ID",
        example: `// GET /api/exams/1\n{ "id": 1, "title": "Math Quiz", "questions": [...] }` },
      { method: "PUT",    path: "/api/exams/:id",      desc: "Update exam title or description",
        example: `// Request body\n{ "title": "Math Quiz — Updated" }` },
      { method: "DELETE", path: "/api/exams/:id",      desc: "Delete exam and all linked data",
        example: `// Response: 204 No Content` },
    ],
  },
  {
    id: "questions",
    label: "Questions",
    icon: FileText,
    color: "text-violet-500",
    endpoints: [
      { method: "GET",  path: "/api/exams/:id/questions", desc: "List all questions for an exam",
        example: `[\n  {\n    "id": 1,\n    "text": "What is 2+2?",\n    "choices": [{"id":1,"text":"3","is_correct":false},{"id":2,"text":"4","is_correct":true}]\n  }\n]` },
      { method: "POST", path: "/api/exams/:id/questions", desc: "Add a question with choices",
        example: `// Request body\n{\n  "text": "Capital of France?",\n  "choices": [\n    {"text":"London","is_correct":false},\n    {"text":"Paris","is_correct":true}\n  ]\n}` },
    ],
  },
  {
    id: "students",
    label: "Students",
    icon: Users,
    color: "text-cyan-500",
    endpoints: [
      { method: "GET",  path: "/api/students",     desc: "List all registered students",
        example: `[\n  { "id": 1, "name": "Amina Benali", "matricule": "20210001", "email": "amina@univ.dz" }\n]` },
      { method: "POST", path: "/api/students",     desc: "Register a new student",
        example: `// Request body\n{ "name": "Yacine Rahmani", "matricule": "20210042", "email": "y.rahmani@univ.dz" }` },
      { method: "GET",  path: "/api/students/:id", desc: "Get a student with their answer history",
        example: `{ "id": 1, "name": "Amina Benali", "answers": [...] }` },
    ],
  },
  {
    id: "scanning",
    label: "Scanning",
    icon: ScanLine,
    color: "text-orange-500",
    endpoints: [
      { method: "POST", path: "/api/scan/upload", desc: "Upload answer sheet image for optical scanning",
        example: `// Multipart form: file (image/pdf) + exam_id (integer)\n// Response\n{\n  "student_id": 5,\n  "exam_id": 1,\n  "answers": { "1": "B", "2": "A", "3": "C" },\n  "confidence": 0.96\n}` },
    ],
  },
  {
    id: "grading",
    label: "Grading & Results",
    icon: BarChart2,
    color: "text-emerald-500",
    endpoints: [
      { method: "GET",  path: "/api/results/exam/:id", desc: "Get all results for an exam",
        example: `[\n  { "student": "Amina Benali", "score": 18, "max_score": 20, "percentage": 90.0, "passed": true }\n]` },
      { method: "POST", path: "/api/results",           desc: "Save a graded result manually",
        example: `// Request body\n{ "student_id": 1, "exam_id": 1, "answers": {"1":"A","2":"B"} }` },
    ],
  },
  {
    id: "ai",
    label: "AI Vision",
    icon: Brain,
    color: "text-pink-500",
    endpoints: [
      { method: "GET",  path: "/api/ai/status",   desc: "Check if the AI model is loaded and ready",
        example: `{ "status": "ready", "model": "Qwen2.5-VL-3B-Instruct", "quantization": "4-bit NF4" }` },
      { method: "POST", path: "/api/ai/ocr",      desc: "Extract handwritten text from image crop",
        example: `// Multipart: file (image)\n// Response\n{ "text": "Le photosynthèse est...", "confidence": 0.88 }` },
      { method: "POST", path: "/api/ai/evaluate", desc: "Score extracted text against model answer",
        example: `// Request body\n{ "student_text": "...", "model_answer": "...", "max_marks": 4 }\n// Response\n{ "score": 3, "feedback": "Good explanation but missed..." }` },
      { method: "POST", path: "/api/ai/correct",  desc: "Submit teacher correction to RAG loop",
        example: `// Request body\n{ "result_id": 12, "corrected_score": 4, "notes": "Full marks — complete answer" }` },
    ],
  },
  {
    id: "health",
    label: "Health",
    icon: Activity,
    color: "text-teal-500",
    endpoints: [
      { method: "GET", path: "/api/health", desc: "Server health check — returns status and uptime",
        example: `{ "status": "ok", "database": "connected", "uptime_seconds": 3600 }` },
    ],
  },
];

const TECH_STACK = [
  { name: "Python 3.10",       version: "3.10",       desc: "Core backend language",               color: "bg-blue-500/10    text-blue-600"    },
  { name: "Flask",             version: "3.1",        desc: "Lightweight REST API framework",       color: "bg-slate-500/10   text-slate-600"   },
  { name: "React",             version: "19",         desc: "Component-driven UI library",          color: "bg-cyan-500/10    text-cyan-600"    },
  { name: "Vite",              version: "6",          desc: "Ultra-fast build tool & dev server",   color: "bg-yellow-500/10  text-yellow-600"  },
  { name: "SQLAlchemy",        version: "2.0",        desc: "Python ORM for SQLite/Postgres",       color: "bg-red-500/10     text-red-600"     },
  { name: "OpenCV",            version: "4.11",       desc: "Computer vision & bubble detection",   color: "bg-green-500/10   text-green-600"   },
  { name: "Qwen2.5-VL-3B",    version: "2.5",        desc: "Vision-language model for OCR/grading",color: "bg-purple-500/10  text-purple-600"  },
  { name: "Tailwind CSS",      version: "4",          desc: "Utility-first styling framework",      color: "bg-teal-500/10    text-teal-600"    },
  { name: "shadcn/ui",         version: "base-nova",  desc: "Accessible component primitives",      color: "bg-zinc-500/10    text-zinc-600"    },
  { name: "TanStack Query",    version: "5",          desc: "Server-state caching & sync",          color: "bg-orange-500/10  text-orange-600"  },
  { name: "Recharts",          version: "2",          desc: "SVG charts for result visualisation",  color: "bg-pink-500/10    text-pink-600"    },
  { name: "BitsAndBytes",      version: "0.43",       desc: "4-bit NF4 model quantisation",         color: "bg-indigo-500/10  text-indigo-600"  },
  { name: "PyJWT",             version: "2.8",        desc: "JSON Web Token auth for Flask API",      color: "bg-yellow-500/10  text-yellow-600"  },
  { name: "bcrypt",            version: "4.1",        desc: "Password hashing for teacher accounts",  color: "bg-amber-500/10   text-amber-600"   },
  { name: "Flask-Limiter",     version: "3.5",        desc: "Rate limiting for API endpoints",        color: "bg-rose-500/10    text-rose-600"    },
  { name: "TensorFlow.js",     version: "4",          desc: "In-browser ML runtime for face detection","color": "bg-orange-500/10 text-orange-600" },
  { name: "BlazeFace",         version: "0.0.7",      desc: "Lightweight face detection model (TFJS)", color: "bg-fuchsia-500/10 text-fuchsia-600" },
  { name: "html5-qrcode",      version: "2.3",        desc: "Barcode & QR scanner for student login",  color: "bg-lime-500/10    text-lime-600"    },
];

const METHOD_STYLES = {
  GET:    { label: "GET",    bg: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400" },
  POST:   { label: "POST",  bg: "bg-blue-500/15 text-blue-700 dark:text-blue-400" },
  PUT:    { label: "PUT",   bg: "bg-amber-500/15 text-amber-700 dark:text-amber-400" },
  DELETE: { label: "DELETE", bg: "bg-red-500/15 text-red-700 dark:text-red-400" },
};

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
      desc: "Step-by-step guide: Python env, CUDA setup, npm install, Docker, run.py — v1.0.0",
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
      action: "Open",
      onClick: () => setMdModal({ open: true, filePath: "docs/thesis/07-appendices.md", title: "Installation Guide" }),
    },
    {
      icon: Users,
      label: "User Manual",
      desc: "End-user manual for teachers: auth, exams, sessions, proctoring, scanning, results",
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
        description="Complete documentation for the SmartGrader REST API, architecture, and tech stack — v1.0.0."
        helpText="Browse all 40+ API endpoints grouped by resource, explore the 5-layer system architecture, and view the full technology stack."
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
              5-Layer System Architecture
            </h3>
            {/* Flow diagram */}
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 flex-wrap">
              {[
                { icon: Globe,    label: "React Frontend",  sub: "Vite · React 19 · TanStack Query · TensorFlow.js",   color: "border-cyan-500/30    bg-cyan-500/10",   text: "text-cyan-600"    },
                { icon: Lock,     label: "Auth Layer",      sub: "PyJWT · bcrypt · Flask-Limiter",     color: "border-yellow-500/30  bg-yellow-500/10", text: "text-yellow-600"  },
                { icon: Server,   label: "Flask API",       sub: "Python 3.10 · Flask 3.1 · Blueprints · 40+ endpoints", color: "border-indigo-500/30  bg-indigo-500/10", text: "text-indigo-500"  },
                { icon: Eye,      label: "Proctor Layer",   sub: "BlazeFace · event tracking · snapshots", color: "border-orange-500/30  bg-orange-500/10", text: "text-orange-500"  },
                { icon: Database, label: "SQLite + AI",     sub: "SQLAlchemy 2.0 · ~15 models · Qwen2.5-VL-3B", color: "border-emerald-500/30 bg-emerald-500/10", text: "text-emerald-600" },
              ].map((tier, i) => {
                const Icon = tier.icon;
                return (
                  <div key={i} className="flex items-center gap-4">
                    <div className={`flex flex-col items-center gap-2 border rounded-xl px-6 py-4 min-w-44 text-center ${tier.color}`}>
                      <Icon className={`h-8 w-8 ${tier.text}`} />
                      <span className="font-heading font-semibold text-sm text-foreground">{tier.label}</span>
                      <span className="text-xs text-muted-foreground">{tier.sub}</span>
                    </div>
                    {i < 4 && <ArrowRight className="h-6 w-6 shrink-0 hidden md:block opacity-40" />}
                    {i < 4 && <ArrowRight className="h-6 w-6 shrink-0 md:hidden rotate-90 opacity-40" />}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "Layered Design",        icon: Layers,  desc: "Routes → Services → Models. Each layer has a single responsibility. Routes are thin HTTP handlers; all business logic lives in services." },
              { title: "JWT Auth Middleware",    icon: Lock,    desc: "Every protected route validates a Bearer JWT via PyJWT. Roles (teacher/student/admin) are encoded in the token payload and enforced at the route level." },
              { title: "Online Exam Engine",     icon: MonitorPlay, desc: "Sessions bind an exam to a student group with a configurable timer. Student answers auto-save every selection; the engine auto-submits on timeout." },
              { title: "Anti-Cheat Proctoring",  icon: Eye,     desc: "Client-side TensorFlow.js + BlazeFace detects face presence. Tab-switch and window-blur events are tracked. Periodic webcam snapshots are stored for review." },
              { title: "Pure Scanner Modules",   icon: ScanLine, desc: "Scanner modules (preprocessor, marker_finder, detector, grid_mapper, answer_reader) are pure image processing with zero DB dependencies." },
              { title: "Custom Exceptions",      icon: Shield,  desc: "app/errors.py defines ScannerError, GradingError, NotFoundError, AuthError with HTTP status codes for consistent JSON error responses." },
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
            <h3 className="font-heading font-semibold mb-4 text-foreground">Directory Structure</h3>
            <pre className="text-xs font-mono leading-relaxed overflow-x-auto text-muted-foreground">{`app/
  __init__.py          # Flask app factory (create_app)
  config.py            # All configuration values
  errors.py            # Custom exceptions with HTTP codes
  models/              # ~15 SQLAlchemy ORM models
    exam.py            → Exam, Question, Choice
    student.py         → Student, StudentAnswer
    result.py          → Result
    auth.py            → Teacher, TokenBlacklist
    group.py           → Group, GroupMembership
    session.py         → ExamSession, SessionAttempt
    proctor.py         → ProctorEvent, ProctorSnapshot
  services/            # Business logic layer
    exam_service.py
    grading_service.py
    scanner_service.py
    session_service.py
    proctor_service.py
  scanner/             # Pure image processing
    preprocessor.py    → Deskew, crop, grayscale, threshold
    marker_finder.py   → Triangle alignment marker detection
    detector.py        → Contour-based bubble detection
    grid_mapper.py     → Map bubbles to question/choice grid
    answer_reader.py   → Read filled answers from grid
  routes/              # Flask blueprints (40+ endpoints)
    auth.py            → /api/auth/*
    admin.py           → /api/admin/*
    groups.py          → /api/groups/*
    sessions.py        → /api/sessions/*
    student_exam.py    → /api/student/exams/*
    proctor.py         → /api/proctor/*
  ai/                  # Qwen2.5-VL integration (Sub-Project 3)
frontend/              # React + Vite SPA
  src/pages/           # Dashboard, Exams, Scanner, Sessions,
                       # Proctoring, StudentExam, Help, Docs...`}</pre>
          </div>
        </div>
      )}

      {/* Tech Stack */}
      {activeTab === "stack" && (
        <div className="space-y-4">
          <div className="glass rounded-xl p-6">
            <h3 className="font-heading font-semibold text-lg mb-4 text-foreground">Full Technology Stack</h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {TECH_STACK.map((tech, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-white/10 hover:bg-white/5 transition-all duration-200">
                  <div className={`rounded-lg p-2 shrink-0 ${tech.color.split(" ")[0]}`}>
                    <Zap className={`h-4 w-4 ${tech.color.split(" ")[1]}`} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm text-foreground">{tech.name}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded bg-white/10 font-mono text-muted-foreground">v{tech.version}</span>
                    </div>
                    <p className="text-xs mt-0.5 text-muted-foreground">{tech.desc}</p>
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
                    <h4 className="font-heading font-semibold text-foreground">{link.label}</h4>
                    <p className="text-xs mt-1 leading-relaxed text-muted-foreground">{link.desc}</p>
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
