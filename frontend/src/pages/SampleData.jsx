import { useState } from "react";
import { JsonPreviewModal } from "@/components/ui/json-preview-modal";
import { ImagePreviewModal } from "@/components/ui/image-preview-modal";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import {
  FileText, FileImage, Printer, ExternalLink, ScanLine, Eye,
  ArrowRight, Key, Download, FolderOpen, ChevronDown, ChevronRight,
  Image, FileJson, FileScan,
} from "lucide-react";

const EXAM_SHEETS = [
  { name: "qcm_exam_1.html",         type: "HTML", desc: "Mathematics \u2014 20 questions, 4 choices each",   file: "qcm_exam_1.html"          },
  { name: "qcm_exam_2.html",         type: "HTML", desc: "Biology \u2014 15 questions, 5 choices each",       file: "qcm_exam_2.html"          },
  { name: "qcm_exam_3.html",         type: "HTML", desc: "Physics \u2014 20 questions, 4 choices each",       file: "qcm_exam_3.html"          },
  { name: "qcm_exam_4.html",         type: "HTML", desc: "Chemistry \u2014 25 questions, 4 choices each",     file: "qcm_exam_4.html"          },
  { name: "qcm_exam_5_final.html",   type: "HTML", desc: "Computer Science \u2014 30 questions, final version",file: "qcm_exam_5_final.html"   },
  { name: "QCM Answer Sheet.pdf",    type: "PDF",  desc: "Generic A4 answer sheet, 20 bubbles per column",file: "QCM Answer Sheet.pdf"   },
  { name: "QCM Answer Sheet v2.pdf", type: "PDF",  desc: "Revised layout with larger bubbles",           file: "QCM Answer Sheet v2.pdf" },
  { name: "QCM Answer Sheet v3.pdf", type: "PDF",  desc: "Final production layout with alignment markers",file: "QCM Answer Sheet v3.pdf"},
];

const SCANNED_SHEETS = [
  { name: "QCM Answer Sheet_page-0001.jpg", desc: "Scanned sheet \u2014 student A, exam 1",  size: "~1.2 MB" },
  { name: "QCM Answer Sheet_page-0002.jpg", desc: "Scanned sheet \u2014 student B, exam 1",  size: "~1.1 MB" },
  { name: "QCM Answer Sheet_page-0003.jpg", desc: "Scanned sheet \u2014 student C, exam 1",  size: "~1.3 MB" },
  { name: "scanned_result.jpg",             desc: "Post-processing result overlay",      size: "~0.8 MB" },
  { name: "test_sheet_filled.jpg",          desc: "Manually filled test sheet",          size: "~1.0 MB" },
  { name: "test_sheet_partial.jpg",         desc: "Partially filled sheet (edge case)",  size: "~0.9 MB" },
];

const PIPELINE_STAGES = [
  { step: "01", label: "Original",          file: "01_original.png",          desc: "Raw scan input",             color: "text-slate-500",   bg: "bg-slate-500/10",   border: "border-slate-500/30"   },
  { step: "02", label: "Grayscale",         file: "02_grayscale.png",         desc: "RGB \u2192 Grayscale conversion", color: "text-zinc-400",    bg: "bg-zinc-400/10",    border: "border-zinc-400/30"    },
  { step: "03", label: "Noise Reduced",     file: "03_noise_reduced.png",     desc: "Gaussian blur applied",      color: "text-blue-500",    bg: "bg-blue-500/10",    border: "border-blue-500/30"    },
  { step: "04", label: "Contrast Enhanced", file: "04_contrast_enhanced.png", desc: "CLAHE equalisation",         color: "text-indigo-500",  bg: "bg-indigo-500/10",  border: "border-indigo-500/30"  },
  { step: "05", label: "Threshold",         file: "05_threshold.png",         desc: "Adaptive binary threshold",  color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
];

const ANSWER_KEYS = [
  { name: "answer_key_exam_1.json", exam: "Exam 1 \u2014 Mathematics",    questions: 20, file: "answer_key_exam_1.json" },
  { name: "answer_key_exam_2.json", exam: "Exam 2 \u2014 Biology",         questions: 15, file: "answer_key_exam_2.json" },
  { name: "answer_key_exam_3.json", exam: "Exam 3 \u2014 Physics",         questions: 20, file: "answer_key_exam_3.json" },
  { name: "answer_key_exam_4.json", exam: "Exam 4 \u2014 Chemistry",       questions: 25, file: "answer_key_exam_4.json" },
  { name: "answer_key_exam_5.json", exam: "Exam 5 \u2014 Computer Science",questions: 30, file: "answer_key_exam_5.json" },
];

function SectionHeader({ icon: Icon, title, count, color }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <Icon className={`h-5 w-5 ${color}`} />
      <h3 className="font-heading font-semibold text-lg text-foreground">{title}</h3>
      {count && (
        <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 font-medium text-muted-foreground">
          {count}
        </span>
      )}
    </div>
  );
}

export default function SampleData() {
  const [expandedKey, setExpandedKey] = useState(null);
  const [jsonModal, setJsonModal] = useState({ open: false, filename: "", title: "" });
  const [imageModal, setImageModal] = useState({ open: false, src: "", title: "" });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Sample Data"
        description="Browse sample exam sheets, scanned answer images, scanner debug output, and answer keys."
        helpText="Pre-generated sample data used for testing the SmartGrader scanner and grading pipeline. Files are stored in old sheets/, old files/, and debug_output/ in the project root."
      />

      {/* Exam Sheet Samples */}
      <section>
        <div className="glass rounded-xl p-6">
          <SectionHeader icon={FileText} title="Exam Sheet Samples" count="8 files" color="text-indigo-500" />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {EXAM_SHEETS.map((sheet, i) => (
              <div key={i} className="border border-white/10 rounded-xl overflow-hidden hover:bg-white/5 transition-all duration-200 flex flex-col">
                {/* Preview area */}
                <div className="h-28 flex flex-col items-center justify-center gap-2 bg-black/20 border-b border-white/10">
                  {sheet.type === "PDF" ? (
                    <FileScan className="h-10 w-10 opacity-30 text-red-400" />
                  ) : (
                    <FileText className="h-10 w-10 opacity-30 text-indigo-400" />
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded font-mono font-bold ${
                    sheet.type === "PDF"
                      ? "bg-red-500/15 text-red-500"
                      : "bg-indigo-500/15 text-indigo-500"
                  }`}>{sheet.type}</span>
                </div>
                {/* Info */}
                <div className="p-3 flex-1 flex flex-col gap-2">
                  <p className="text-xs font-mono font-medium leading-tight text-foreground">
                    {sheet.name}
                  </p>
                  <p className="text-xs flex-1 text-muted-foreground">{sheet.desc}</p>
                  <div className="flex gap-2 mt-auto pt-1">
                    <button
                      onClick={() => window.open(`/api/files/old files/${sheet.file}`, "_blank")}
                      className="flex-1 flex items-center justify-center gap-1 text-xs py-1.5 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200 text-muted-foreground"
                    >
                      <ExternalLink className="h-3 w-3" /> Open
                    </button>
                    <button
                      onClick={() => {
                        const win = window.open(`/api/files/old files/${sheet.file}`, "_blank");
                        if (win) win.onload = () => win.print();
                      }}
                      className="flex items-center justify-center gap-1 text-xs py-1.5 px-2 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200 text-muted-foreground"
                    >
                      <Printer className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scanned Sheet Samples */}
      <section>
        <div className="glass rounded-xl p-6">
          <SectionHeader icon={ScanLine} title="Scanned Sheet Samples" count="6 images" color="text-cyan-500" />
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {SCANNED_SHEETS.map((sheet, i) => (
              <div key={i} className="border border-white/10 rounded-xl overflow-hidden hover:bg-white/5 transition-all duration-200 flex flex-col">
                {/* Thumbnail placeholder */}
                <div className="h-32 flex flex-col items-center justify-center gap-2 bg-black/20 border-b border-white/10">
                  <Image className="h-10 w-10 opacity-25 text-cyan-400" />
                  <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-500 font-mono font-bold">JPG</span>
                </div>
                <div className="p-3 flex flex-col gap-1">
                  <p className="text-xs font-mono font-medium leading-tight text-foreground">
                    {sheet.name}
                  </p>
                  <p className="text-xs text-muted-foreground">{sheet.desc}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs opacity-50">{sheet.size}</span>
                    <button
                      onClick={() => setImageModal({ open: true, src: `/api/files/old sheets/${sheet.name}`, title: sheet.name })}
                      className="flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200 text-muted-foreground"
                    >
                      <Eye className="h-3 w-3" /> View
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs mt-3 text-muted-foreground">
            Files located in <code className="font-mono bg-black/20 px-1 rounded">old sheets/</code> directory. Serve with a static file server to preview.
          </p>
        </div>
      </section>

      {/* Debug Pipeline Output */}
      <section>
        <div className="glass rounded-xl p-6">
          <SectionHeader icon={FolderOpen} title="Scanner Debug Pipeline Output" count="5 stages" color="text-orange-500" />
          <p className="text-xs mb-4 text-muted-foreground">
            Images in <code className="font-mono bg-black/20 px-1 rounded">debug_output/</code> show each preprocessing stage. Generated when
            <code className="font-mono bg-black/20 px-1 rounded ml-1">DEBUG_SCANNER=True</code>.
          </p>
          <div className="flex flex-col sm:flex-row gap-2 items-stretch">
            {PIPELINE_STAGES.map((stage, i) => (
              <div key={i} className="flex items-stretch gap-2 flex-1">
                <div className={`flex-1 rounded-xl border ${stage.border} ${stage.bg} p-4 flex flex-col items-center text-center gap-2`}>
                  <span className={`text-xs font-mono font-bold ${stage.color}`}>{stage.step}</span>
                  <div className={`w-12 h-12 rounded-lg ${stage.bg} flex items-center justify-center border ${stage.border}`}>
                    <Image className={`h-6 w-6 ${stage.color} opacity-70`} />
                  </div>
                  <span className="font-heading font-semibold text-xs text-foreground">{stage.label}</span>
                  <span className="text-xs text-muted-foreground">{stage.desc}</span>
                  <button
                    onClick={() => setImageModal({ open: true, src: `/api/files/debug_output/${stage.file}`, title: stage.label })}
                    className={`text-xs px-2 py-1 rounded-lg border ${stage.border} hover:opacity-80 cursor-pointer transition-all duration-200 ${stage.color}`}
                  >
                    View
                  </button>
                </div>
                {i < PIPELINE_STAGES.length - 1 && (
                  <ArrowRight className="h-4 w-4 self-center shrink-0 opacity-25 hidden sm:block" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Answer Keys */}
      <section>
        <div className="glass rounded-xl p-6">
          <SectionHeader icon={Key} title="Answer Keys" count="5 JSON files" color="text-emerald-500" />
          <div className="space-y-2">
            {ANSWER_KEYS.map((key, idx) => {
              const isOpen = expandedKey === idx;
              return (
                <div key={idx} className="border border-white/10 rounded-xl overflow-hidden">
                  <button
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-all duration-200 cursor-pointer text-left"
                    onClick={() => setExpandedKey(isOpen ? null : idx)}
                  >
                    <FileJson className="h-4 w-4 text-emerald-500 shrink-0" />
                    <code className="text-sm font-mono flex-1 text-foreground">{key.name}</code>
                    <span className="text-xs text-muted-foreground">{key.exam}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-medium">
                      {key.questions}Q
                    </span>
                    {isOpen ? <ChevronDown className="h-4 w-4 opacity-40" /> : <ChevronRight className="h-4 w-4 opacity-40" />}
                  </button>
                  {isOpen && (
                    <div className="border-t border-white/10 px-4 py-3 bg-black/10">
                      <pre className="text-xs font-mono text-muted-foreground">{`{
  "exam_id": ${idx + 1},
  "exam_title": "...",
  "total_questions": ${key.questions},
  "answers": {
    "1": {
      "question_number": 1,
      "correct_answer": "A",
      "question_text": "..."
    }
  }
}`}</pre>
                      <div className="flex gap-2 mt-3">
                        <button
                          onClick={() => setJsonModal({ open: true, filename: key.file, title: key.file })}
                          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200 text-muted-foreground"
                        >
                          <Eye className="h-3 w-3" /> View Full JSON
                        </button>
                        <button
                          onClick={() => alert("Feature coming soon \u2014 requires static file serving to be configured.")}
                          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200 text-muted-foreground"
                        >
                          <Download className="h-3 w-3" /> Download
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          <p className="text-xs mt-3 text-muted-foreground">
            Located in <code className="font-mono bg-black/20 px-1 rounded">old sheets/</code>. Use these keys with the
            <code className="font-mono bg-black/20 px-1 rounded ml-1">POST /api/results</code> endpoint for manual grading validation.
          </p>
        </div>
      </section>

      <JsonPreviewModal
        open={jsonModal.open}
        onClose={() => setJsonModal({ open: false, filename: "", title: "" })}
        filename={jsonModal.filename}
        title={jsonModal.title}
      />

      <ImagePreviewModal
        open={imageModal.open}
        onClose={() => setImageModal({ open: false, src: "", title: "" })}
        src={imageModal.src}
        title={imageModal.title}
      />
    </div>
  );
}
