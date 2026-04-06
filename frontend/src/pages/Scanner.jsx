import { useState } from "react";
import { ScanLine, Brain, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useExams, useExamQuestions } from "@/hooks/use-exams";
import { uploadFile } from "@/lib/api";
import { useOCR, useEvaluate } from "@/hooks/use-ai";
import UploadZone from "@/components/scanner/UploadZone";
import ScanResults from "@/components/scanner/ScanResults";
import OCRResults from "@/components/scanner/OCRResults";
import AIGradeResults from "@/components/scanner/AIGradeResults";

export default function Scanner() {
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

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold font-heading">Scanner</h2>

      <Tabs defaultValue="mcq">
        <TabsList>
          <TabsTrigger value="mcq" className="cursor-pointer">
            <ScanLine className="mr-2 h-4 w-4" /> MCQ Scanning
          </TabsTrigger>
          <TabsTrigger value="ai" className="cursor-pointer">
            <Brain className="mr-2 h-4 w-4" /> Short Answer Grading
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mcq" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="font-heading text-base">Scan MCQ Sheet</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Select Exam *</Label>
                <Select value={examId} onValueChange={setExamId}>
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
              </div>
              <UploadZone file={file} onFileChange={setFile} />
              <Button
                onClick={handleMCQScan}
                disabled={!file || !examId || scanning}
                className="w-full cursor-pointer"
              >
                {scanning ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Scanning...</>
                ) : (
                  <><ScanLine className="mr-2 h-4 w-4" /> Scan & Grade</>
                )}
              </Button>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </CardContent>
          </Card>
          {mcqResult && <ScanResults result={mcqResult} />}
        </TabsContent>

        <TabsContent value="ai" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="font-heading text-base">AI Short Answer Grading</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Select Exam *</Label>
                <Select value={examId} onValueChange={(v) => { setExamId(v); setOcrAnswers(null); setAiGrades(null); }}>
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
              </div>
              <UploadZone file={file} onFileChange={setFile} />
              <Button
                onClick={handleExtractAnswers}
                disabled={!file || !examId || ocrMutation.isPending}
                className="w-full cursor-pointer"
              >
                {ocrMutation.isPending ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Extracting...</>
                ) : (
                  <><Brain className="mr-2 h-4 w-4" /> Extract Answers (OCR)</>
                )}
              </Button>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </CardContent>
          </Card>

          {ocrAnswers && (
            <>
              <OCRResults answers={ocrAnswers} onUpdateAnswer={updateOCRAnswer} />
              <Button
                onClick={handleGradeAll}
                disabled={evaluateMutation.isPending}
                className="w-full cursor-pointer"
              >
                {evaluateMutation.isPending ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Grading...</>
                ) : (
                  "Grade All Answers"
                )}
              </Button>
            </>
          )}

          {aiGrades && <AIGradeResults grades={aiGrades} answers={ocrAnswers || []} />}
        </TabsContent>
      </Tabs>
    </div>
  );
}
