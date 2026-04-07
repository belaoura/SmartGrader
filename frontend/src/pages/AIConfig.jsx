import { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Brain, Cpu, Zap, AlertTriangle, ChevronDown, ChevronRight,
  ArrowRight, ScanLine, Eye, MessageSquare, RefreshCw,
  Settings2, Sliders, Activity, Server, Info,
} from "lucide-react";

const CONFIG_PARAMS = [
  {
    key: "CONFIDENCE_THRESHOLD", value: "0.7", type: "float", category: "AI",
    desc: "AI grades below this score are flagged for teacher review. Prevents over-confident incorrect automated grading.",
    color: "text-pink-500", bg: "bg-pink-500/10",
  },
  {
    key: "FILL_THRESHOLD", value: "0.35", type: "float", category: "Scanner",
    desc: "Minimum fill ratio for a bubble to be considered 'filled'. Ratio of dark pixels in the bubble ROI.",
    color: "text-orange-500", bg: "bg-orange-500/10",
  },
  {
    key: "CIRCLE_AREA_MIN", value: "100", type: "int", category: "Scanner",
    desc: "Minimum contour area (px²) for a region to be considered a bubble. Filters out noise and artefacts.",
    color: "text-amber-500", bg: "bg-amber-500/10",
  },
  {
    key: "CIRCLE_AREA_MAX", value: "5000", type: "int", category: "Scanner",
    desc: "Maximum contour area (px²). Excludes large shapes that are clearly not answer bubbles.",
    color: "text-yellow-500", bg: "bg-yellow-500/10",
  },
  {
    key: "CIRCULARITY_MIN", value: "0.5", type: "float", category: "Scanner",
    desc: "Minimum circularity score (4π·area/perimeter²). Rejects non-circular contours.",
    color: "text-lime-500", bg: "bg-lime-500/10",
  },
];

const SCANNER_STAGES = [
  {
    step: "01", label: "Preprocessing",
    icon: Eye, color: "text-indigo-500", bg: "bg-indigo-500/10", border: "border-indigo-500/30",
    detail: "Deskew → Crop → Grayscale → Threshold",
    file: "scanner/preprocessor.py",
  },
  {
    step: "02", label: "Marker Detection",
    icon: ScanLine, color: "text-violet-500", bg: "bg-violet-500/10", border: "border-violet-500/30",
    detail: "Detect triangle alignment markers for sheet registration",
    file: "scanner/marker_finder.py",
  },
  {
    step: "03", label: "Bubble Detection",
    icon: Activity, color: "text-cyan-500", bg: "bg-cyan-500/10", border: "border-cyan-500/30",
    detail: "Contour-based detection with area + circularity filters",
    file: "scanner/detector.py",
  },
  {
    step: "04", label: "Grid Mapping",
    icon: Sliders, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30",
    detail: "Map detected bubbles to question/choice grid coordinates",
    file: "scanner/grid_mapper.py",
  },
  {
    step: "05", label: "Answer Reading",
    icon: Brain, color: "text-pink-500", bg: "bg-pink-500/10", border: "border-pink-500/30",
    detail: "Apply FILL_THRESHOLD to determine selected answers",
    file: "scanner/answer_reader.py",
  },
];

const REQUIREMENTS = [
  { label: "CUDA-compatible GPU",     detail: "NVIDIA RTX / Tesla with CUDA 11.8+",  icon: Cpu,       color: "text-indigo-500" },
  { label: "~6-8 GB VRAM",           detail: "Minimum for 4-bit quantised Qwen2.5",  icon: Server,    color: "text-pink-500"   },
  { label: "Python 3.10+",           detail: "Required for transformers compatibility",icon: Zap,       color: "text-amber-500"  },
  { label: "PyTorch + CUDA",         detail: "torch>=2.0 built with CUDA support",    icon: Activity,  color: "text-cyan-500"   },
  { label: "transformers library",   detail: "HuggingFace transformers ≥4.45",        icon: Brain,     color: "text-emerald-500" },
  { label: "BitsAndBytes 0.43",      detail: "4-bit NF4 quantisation backend",        icon: Settings2, color: "text-violet-500" },
];

function ExpandSection({ title, icon: Icon, color, children }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="glass rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-6 py-4 cursor-pointer hover:bg-white/5 transition-all duration-200"
        onClick={() => setOpen((v) => !v)}
      >
        <Icon className={`h-5 w-5 ${color}`} />
        <span className="font-heading font-semibold text-base flex-1 text-left text-foreground">
          {title}
        </span>
        {open ? <ChevronDown className="h-4 w-4 opacity-40" /> : <ChevronRight className="h-4 w-4 opacity-40" />}
      </button>
      {open && <div className="px-6 pb-6 pt-0">{children}</div>}
    </div>
  );
}

export default function AIConfig() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Configuration"
        description="Read-only view of the current AI model settings from app/config.py."
        helpText="Displays the Qwen2.5-VL model configuration, scanner thresholds, AI pipeline stages, and GPU requirements. Edit values directly in app/config.py."
      />

      {/* Notice banner */}
      <div className="glass rounded-xl p-4 flex items-center gap-3 border border-amber-500/30 bg-amber-500/5">
        <Info className="h-5 w-5 text-amber-500 shrink-0" />
        <p className="text-sm text-muted-foreground">
          This is a <strong className="text-foreground">read-only</strong> display of configuration values from{" "}
          <code className="font-mono text-xs bg-black/20 px-1 rounded">app/config.py</code>. A live config API is planned for a future release.
        </p>
      </div>

      {/* Model Status Card */}
      <ExpandSection title="Model Status" icon={Brain} color="text-pink-500">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mt-4">
          {[
            { label: "Model",         value: "Qwen2.5-VL-3B-Instruct",  icon: Brain,     color: "text-pink-500",    bg: "bg-pink-500/10"    },
            { label: "Quantisation",  value: "4-bit NF4",                icon: Cpu,       color: "text-violet-500",  bg: "bg-violet-500/10"  },
            { label: "Status",        value: "Requires GPU",             icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
            { label: "VRAM Required", value: "~6–8 GB",                  icon: Server,    color: "text-indigo-500",  bg: "bg-indigo-500/10"  },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className={`rounded-xl p-4 border border-white/10 ${stat.bg} flex flex-col gap-2`}>
                <div className="flex items-center gap-2">
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                  <span className="text-xs font-medium text-muted-foreground">{stat.label}</span>
                </div>
                <span className={`font-heading font-semibold text-sm ${stat.color}`}>{stat.value}</span>
              </div>
            );
          })}
        </div>

        <div className="mt-4 p-4 rounded-lg bg-black/10 border border-white/5 space-y-2">
          <p className="text-xs font-medium text-muted-foreground">HuggingFace model path:</p>
          <code className="text-sm font-mono text-primary">Qwen/Qwen2.5-VL-3B-Instruct</code>
          <p className="text-xs text-muted-foreground">
            Downloaded automatically on first run via <code className="font-mono bg-black/20 px-1 rounded text-xs">transformers.AutoModelForVision2Seq</code>.
            Cached to <code className="font-mono bg-black/20 px-1 rounded text-xs">~/.cache/huggingface/</code>.
          </p>
        </div>
      </ExpandSection>

      {/* AI Pipeline */}
      <ExpandSection title="AI Pipeline Configuration" icon={Zap} color="text-indigo-500">
        <div className="mt-4 space-y-4">
          {/* Stage 1 */}
          <div className="flex flex-col sm:flex-row gap-4 items-stretch">
            {[
              {
                stage: "Stage 1", label: "OCR", icon: Eye, color: "text-cyan-500", bg: "bg-cyan-500/10", border: "border-cyan-500/30",
                desc: "Handwritten text extraction from cropped answer image",
                params: [["Model", "Qwen2.5-VL-3B-Instruct"], ["max_new_tokens", "512"], ["Task prompt", "\"Extract text...\""]],
              },
              {
                stage: "Stage 2", label: "Evaluation", icon: MessageSquare, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30",
                desc: "Score extracted text against model answer or keywords",
                params: [["Mode", "model_answer / keywords"], ["max_marks", "configurable per question"], ["output", "score + feedback"]],
              },
              {
                stage: "Stage 3", label: "RAG Feedback Loop", icon: RefreshCw, color: "text-pink-500", bg: "bg-pink-500/10", border: "border-pink-500/30",
                desc: "Teacher corrections stored and used to improve future grading",
                params: [["Table", "ai_corrections"], ["Trigger", "POST /api/ai/correct"], ["Effect", "Retrieval-augmented re-evaluation"]],
              },
            ].map((stage, i) => {
              const Icon = stage.icon;
              return (
                <div key={i} className="flex items-stretch gap-3 flex-1">
                  <div className={`flex-1 rounded-xl p-4 border ${stage.border} ${stage.bg}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-mono opacity-60">{stage.stage}</span>
                      <Icon className={`h-4 w-4 ${stage.color}`} />
                      <span className="font-heading font-semibold text-sm text-foreground">{stage.label}</span>
                    </div>
                    <p className="text-xs mb-3 text-muted-foreground">{stage.desc}</p>
                    <div className="space-y-1">
                      {stage.params.map(([k, v]) => (
                        <div key={k} className="flex justify-between text-xs gap-2">
                          <span className="font-mono opacity-60">{k}:</span>
                          <span className="font-medium text-right text-foreground">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {i < 2 && <ArrowRight className="h-5 w-5 shrink-0 self-center opacity-30 hidden sm:block" />}
                </div>
              );
            })}
          </div>
        </div>
      </ExpandSection>

      {/* Thresholds & Parameters */}
      <ExpandSection title="Thresholds & Parameters" icon={Sliders} color="text-amber-500">
        <div className="mt-4 space-y-2">
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 mb-4">
            {CONFIG_PARAMS.map((p) => (
              <div key={p.key} className={`rounded-xl p-4 border border-white/10 ${p.bg}`}>
                <div className="flex items-center justify-between gap-2 mb-1">
                  <code className={`text-xs font-mono font-bold ${p.color}`}>{p.key}</code>
                  <div className="flex items-center gap-1">
                    <span className={`text-lg font-heading font-bold ${p.color}`}>{p.value}</span>
                    <span className="text-xs opacity-50 font-mono">{p.type}</span>
                  </div>
                </div>
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${p.bg} ${p.color} border border-current/20`}>{p.category}</span>
                <p className="text-xs mt-2 leading-relaxed text-muted-foreground">{p.desc}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            All values configurable in <code className="font-mono bg-black/20 px-1 rounded">app/config.py</code> under the <code className="font-mono bg-black/20 px-1 rounded">Config</code> base class.
          </p>
        </div>
      </ExpandSection>

      {/* Scanner Pipeline */}
      <ExpandSection title="Scanner Pipeline" icon={ScanLine} color="text-cyan-500">
        <div className="mt-4 space-y-3">
          <div className="flex flex-col gap-3">
            {SCANNER_STAGES.map((stage, i) => {
              const Icon = stage.icon;
              return (
                <div key={i} className="flex items-stretch gap-3">
                  <div className={`flex-1 rounded-xl p-4 border ${stage.border} ${stage.bg} flex items-start gap-3`}>
                    <div className={`rounded-lg p-2 ${stage.bg} shrink-0`}>
                      <Icon className={`h-4 w-4 ${stage.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-mono text-xs opacity-50">{stage.step}</span>
                        <span className="font-heading font-semibold text-sm text-foreground">{stage.label}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{stage.detail}</p>
                      <code className="text-xs font-mono opacity-40 mt-1 block">{stage.file}</code>
                    </div>
                    {i < SCANNER_STAGES.length - 1 && (
                      <div className="hidden lg:flex items-center">
                        <ArrowRight className="h-4 w-4 opacity-30" />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-3 p-3 rounded-lg bg-black/10 border border-white/5">
            <p className="text-xs text-muted-foreground">
              Debug images for each stage are saved to <code className="font-mono bg-black/20 px-1 rounded">debug_output/</code> when
              <code className="font-mono bg-black/20 px-1 rounded ml-1">DEBUG_SCANNER=True</code> in config.
            </p>
          </div>
        </div>
      </ExpandSection>

      {/* Requirements */}
      <ExpandSection title="Hardware & Software Requirements" icon={Server} color="text-violet-500">
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {REQUIREMENTS.map((req, i) => {
            const Icon = req.icon;
            return (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-white/10 bg-black/10">
                <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${req.color}`} />
                <div>
                  <p className="text-sm font-medium text-foreground">{req.label}</p>
                  <p className="text-xs text-muted-foreground">{req.detail}</p>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-4 p-4 rounded-lg bg-amber-500/5 border border-amber-500/20">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
            <p className="text-xs leading-relaxed text-muted-foreground">
              Without a CUDA-compatible GPU, the AI grading pipeline will fall back to CPU inference which is significantly slower (~3-5 minutes per answer vs ~10 seconds on GPU). MCQ optical scanning works without GPU.
            </p>
          </div>
        </div>
      </ExpandSection>
    </div>
  );
}
