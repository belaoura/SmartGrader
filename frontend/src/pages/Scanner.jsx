import { useState } from "react";
import { ScanLine, Brain, Loader2, AlertCircle, CheckCircle, Upload, FileText, Zap, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/ui/page-header";
import { useExams, useExamQuestions } from "@/hooks/use-exams";
import { uploadFile } from "@/lib/api";
import { useOCR, useEvaluate } from "@/hooks/use-ai";
import UploadZone from "@/components/scanner/UploadZone";
import ScanResults from "@/components/scanner/ScanResults";
import OCRResults from "@/components/scanner/OCRResults";
import AIGradeResults from "@/components/scanner/AIGradeResults";

function StepProgress({ steps, current }) {
  return (
    <div className="flex items-center w-full">
      {steps.map((step, i) => {
        const isActive = i === current;
        const isDone = i < current;
        return (
          <div key={i} className="flex items-center flex-1 last:flex-initial">
            <div className="flex flex-col items-center gap-1.5">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                isDone ? "bg-emerald-500 text-white" :
                isActive ? "bg-primary text-white ring-4 ring-primary/20" :
                "bg-muted text-muted-foreground"
              }`}>
                {isDone ? <CheckCircle className="h-4 w-4" /> : i + 1}
              </div>
              <span className={`text-[10px] font-medium whitespace-nowrap ${
                isActive ? "text-primary" : isDone ? "text-emerald-600" : "text-muted-foreground"
              }`}>{step}</span>
            </div>
            {i < steps.length - 1 && (
              <div className={`flex-1 h-0.5 mx-2 rounded-full transition-all duration-300 ${
                isDone ? "bg-emerald-500" : "bg-border"
              }`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

function ErrorAlert({ message }) {
  if (!message) return null;
  return (
    <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
      <span>{message}</span>
    </div>
  );
}

function ModeCard({ icon: Icon, title, description, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-start gap-4 p-5 rounded-xl border-2 text-left cursor-pointer transition-all duration-200 hover:-translate-y-0.5 ${
        active
          ? "border-primary bg-primary/5 shadow-lg shadow-primary/10"
          : "border-border bg-card hover:border-primary/30"
      }`}
    >
      <div className={`rounded-xl p-3 ${active ? "bg-primary/15" : "bg-muted"}`}>
        <Icon className={`h-6 w-6 ${active ? "text-primary" : "text-muted-foreground"}`} />
      </div>
      <div>
        <h3 className="font-heading font-semibold text-sm">{title}</h3>
        <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{description}</p>
      </div>
    </button>
  );
}

export default function Scanner() {
  const [mode, setMode] = useState("mcq");
  const [examId, setExamId] = useState("");
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [mcqResult, setMcqResult] = useState(null);
  const [ocrAnswers, setOcrAnswers] = useState(null);
  const [aiGrades, setAiGrades] = useState(null);
  const [error, setError] = useState(null);

  const { data: exams } = useExams();
  const { data: questions } = useExamQuestions(examId || undefined);
  const ocrMutation = useOCR();
  const evaluateMutation = useEvaluate();

  const mcqStep = !examId ? 0 : !file ? 1 : mcqResult ? 2 : 2;
  const aiStep = !examId ? 0 : !file ? 1 : ocrAnswers ? (aiGrades ? 4 : 3) : 2;

  const handleMCQScan = async () => {
    if (!file || !examId) return;
    setScanning(true);
    setError(null);
    setMcqResult(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("exam_id", examId);
    try {
      const data = await uploadFile("/scan/upload", formData);
      setMcqResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setScanning(false);
    }
  };

  const handleExtractAnswers = () => {
    if (!file || !questions) return;
    setError(null);
    setOcrAnswers(null);
    setAiGrades(null);
    const questionIds = questions.map((q) => q.id);
    ocrMutation.mutate(
      { file, questionIds },
      {
        onSuccess: (data) => setOcrAnswers(data.answers),
        onError: (err) => setError(err.message),
      }
    );
  };

  const handleGradeAll = () => {
    if (!ocrAnswers || !questions) return;
    setError(null);
    const answersData = ocrAnswers.map((a) => {
      const q = questions.find((qq) => qq.id === a.question_id);
      return {
        question_id: a.question_id,
        text: a.text,
        question_text: q?.question_text || "",
        max_marks: q?.marks || 0,
        mode: "model_answer",
        reference: "",
      };
    });
    evaluateMutation.mutate(
      { answers: answersData },
      {
        onSuccess: (data) => setAiGrades(data.grades),
        onError: (err) => setError(err.message),
      }
    );
  };

  const updateOCRAnswer = (questionId, text) => {
    setOcrAnswers((prev) =>
      prev.map((a) => (a.question_id === questionId ? { ...a, text } : a))
    );
  };

  const selectedExam = exams?.find(e => String(e.id) === examId);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scanner"
        description="Scan and grade exam answer sheets"
        helpText="MCQ mode uses computer vision (OpenCV) to detect filled bubbles. AI mode uses Qwen2.5-VL to extract and evaluate written answers."
      />

      {/* Mode Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ModeCard
          icon={ScanLine}
          title="MCQ Optical Scanning"
          description="Scan printed bubble sheets using computer vision. Detects filled circles and auto-grades against the answer key."
          active={mode === "mcq"}
          onClick={() => { setMode("mcq"); setMcqResult(null); setError(null); }}
        />
        <ModeCard
          icon={Brain}
          title="AI Short Answer Grading"
          description="Use Qwen2.5-VL vision model to read handwritten answers and score them against exam criteria."
          active={mode === "ai"}
          onClick={() => { setMode("ai"); setOcrAnswers(null); setAiGrades(null); setError(null); }}
        />
      </div>

      {/* Step Progress */}
      <div className="glass rounded-xl px-6 py-4">
        {mode === "mcq" ? (
          <StepProgress steps={["Select Exam", "Upload Sheet", "Scan & Grade"]} current={mcqStep} />
        ) : (
          <StepProgress steps={["Select Exam", "Upload Sheet", "Extract OCR", "Evaluate", "Review"]} current={aiStep} />
        )}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Controls */}
        <div className="lg:col-span-2 space-y-4">
          {/* Exam Selector */}
          <div className="glass rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                <FileText className="h-3.5 w-3.5 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-sm">Select Exam</h3>
            </div>
            <Select value={examId} onValueChange={(v) => { setExamId(v); setMcqResult(null); setOcrAnswers(null); setAiGrades(null); }}>
              <SelectTrigger className="cursor-pointer">
                <SelectValue placeholder="Choose an exam..." />
              </SelectTrigger>
              <SelectContent>
                {(exams || []).map((e) => (
                  <SelectItem key={e.id} value={String(e.id)} className="cursor-pointer">
                    {e.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedExam && (
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="text-xs">{selectedExam.subject}</Badge>
                <Badge variant="secondary" className="text-xs">{selectedExam.total_marks} marks</Badge>
                <Badge variant="secondary" className="text-xs">{selectedExam.statistics?.question_count || "?"} questions</Badge>
              </div>
            )}
          </div>

          {/* Upload */}
          <div className="glass rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                <Upload className="h-3.5 w-3.5 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-sm">Upload Answer Sheet</h3>
            </div>
            <UploadZone file={file} onFileChange={setFile} />
          </div>

          {/* Action Button */}
          {mode === "mcq" ? (
            <Button
              onClick={handleMCQScan}
              disabled={!file || !examId || scanning}
              size="lg"
              className="w-full cursor-pointer hover:-translate-y-0.5 transition-all duration-200 h-12 text-sm font-semibold"
            >
              {scanning ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing scan...</>
              ) : (
                <><Zap className="mr-2 h-4 w-4" /> Scan & Grade</>
              )}
            </Button>
          ) : (
            <div className="space-y-2">
              <Button
                onClick={handleExtractAnswers}
                disabled={!file || !examId || ocrMutation.isPending}
                size="lg"
                className="w-full cursor-pointer hover:-translate-y-0.5 transition-all duration-200 h-12 text-sm font-semibold"
              >
                {ocrMutation.isPending ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Extracting text...</>
                ) : (
                  <><Eye className="mr-2 h-4 w-4" /> Extract Answers (OCR)</>
                )}
              </Button>
              {ocrAnswers && (
                <Button
                  onClick={handleGradeAll}
                  disabled={evaluateMutation.isPending}
                  variant="outline"
                  size="lg"
                  className="w-full cursor-pointer hover:-translate-y-0.5 transition-all duration-200 h-12 text-sm font-semibold border-primary text-primary hover:bg-primary/5"
                >
                  {evaluateMutation.isPending ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Grading...</>
                  ) : (
                    <><Brain className="mr-2 h-4 w-4" /> Grade All Answers</>
                  )}
                </Button>
              )}
            </div>
          )}

          <ErrorAlert message={error} />
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-3 space-y-4">
          {/* Empty state */}
          {mode === "mcq" && !mcqResult && !scanning && (
            <div className="glass rounded-xl flex flex-col items-center justify-center py-20 text-center">
              <div className="rounded-2xl bg-primary/10 p-5 mb-4">
                <ScanLine className="h-10 w-10 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-lg">Ready to Scan</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-xs">
                Select an exam and upload a filled answer sheet to begin scanning.
              </p>
            </div>
          )}

          {mode === "ai" && !ocrAnswers && !ocrMutation.isPending && (
            <div className="glass rounded-xl flex flex-col items-center justify-center py-20 text-center">
              <div className="rounded-2xl bg-primary/10 p-5 mb-4">
                <Brain className="h-10 w-10 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-lg">AI Grading Ready</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-xs">
                Select an exam and upload a student's answer sheet, then click Extract to begin.
              </p>
            </div>
          )}

          {/* Loading states */}
          {scanning && (
            <div className="glass rounded-xl flex flex-col items-center justify-center py-20 text-center">
              <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
              <h3 className="font-heading font-semibold">Processing...</h3>
              <p className="text-sm text-muted-foreground mt-1">Detecting bubbles and matching answers</p>
            </div>
          )}

          {ocrMutation.isPending && (
            <div className="glass rounded-xl flex flex-col items-center justify-center py-20 text-center">
              <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
              <h3 className="font-heading font-semibold">Extracting Text...</h3>
              <p className="text-sm text-muted-foreground mt-1">Reading handwritten answers with AI vision model</p>
            </div>
          )}

          {/* MCQ Results */}
          {mcqResult && <ScanResults result={mcqResult} />}

          {/* OCR Results */}
          {ocrAnswers && <OCRResults answers={ocrAnswers} onUpdateAnswer={updateOCRAnswer} />}

          {/* AI Grades */}
          {aiGrades && <AIGradeResults grades={aiGrades} answers={ocrAnswers || []} />}
        </div>
      </div>
    </div>
  );
}
