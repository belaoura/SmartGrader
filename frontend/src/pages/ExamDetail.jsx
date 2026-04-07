import { useState } from "react";
import { useParams } from "react-router-dom";
import { Plus, CheckCircle2, Printer, FileDown, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { useExam, useExamQuestions } from "@/hooks/use-exams";
import QuestionBuilder from "@/components/exams/QuestionBuilder";

export default function ExamDetail() {
  const { id } = useParams();
  const [builderOpen, setBuilderOpen] = useState(false);
  const { data: exam, isLoading: examLoading } = useExam(id);
  const { data: questions, isLoading: questionsLoading } = useExamQuestions(id);

  if (examLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-16 rounded-lg" />
        <Skeleton className="h-64 rounded-lg" />
      </div>
    );
  }

  const totalMarks = questions?.reduce((s, q) => s + (q.marks || 0), 0) || 0;
  const subjects = exam?.subject ? [exam.subject] : [];

  return (
    <div className="space-y-6">
      <PageHeader
        title={exam?.title || "Exam"}
        description={[exam?.subject, exam?.date].filter(Boolean).join(" | ")}
        helpText="Manage questions for this exam. Each question can have multiple choices with one correct answer."
      >
        <Button
          variant="outline"
          onClick={() => window.print()}
          className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
        >
          <Printer className="mr-2 h-4 w-4" /> Print
        </Button>
        <Button
          variant="outline"
          onClick={() => {
  if (!exam || !questions?.length) return;
  const win = window.open("", "_blank");
  const questionsHtml = questions.map((q, i) => {
    const choiceItems = q.choices?.map((c) =>
      `<div style="display:inline-block;width:48%;margin:2px 0;padding:4px 8px;border-radius:4px;${c.is_correct ? "background:#dcfce7;font-weight:600;" : "background:#f1f5f9;"}">
        <strong>${c.label}.</strong> ${c.text}${c.is_correct ? " ✓" : ""}
      </div>`
    ).join("") || "";
    return `<div style="margin-bottom:16px;page-break-inside:avoid;">
      <p style="font-weight:600;margin-bottom:4px;">Q${i + 1}. ${q.question_text} <span style="color:#6366F1;">(${q.marks} pts)</span></p>
      <div>${choiceItems}</div>
    </div>`;
  }).join("");

  win.document.write(`<!DOCTYPE html><html><head><title>${exam.title} - Answer Key</title>
    <style>
      body { font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.5; max-width: 21cm; margin: 0 auto; padding: 2cm; color: #1a1a1a; }
      h1 { font-size: 18pt; border-bottom: 2px solid #6366F1; padding-bottom: 8px; }
      .meta { color: #64748B; margin-bottom: 24px; }
      @page { size: A4; margin: 2cm; }
    </style></head><body>
    <h1>${exam.title}</h1>
    <p class="meta">${exam.subject || ""} ${exam.date ? "| " + exam.date : ""} | ${questions.length} Questions | ${questions.reduce((s, q) => s + (q.marks || 0), 0)} Total Marks</p>
    ${questionsHtml}
  </body></html>`);
  win.document.close();
  win.onload = () => win.print();
}}
          className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
        >
          <FileDown className="mr-2 h-4 w-4" /> Export PDF
        </Button>
        <Button
          onClick={() => setBuilderOpen(true)}
          className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Question
        </Button>
      </PageHeader>

      {/* Stats summary bar */}
      <div className="glass rounded-xl px-5 py-3 flex flex-wrap items-center gap-3">
        <Badge variant="secondary" className="text-sm px-3 py-1">
          {exam?.statistics?.question_count || 0} Questions
        </Badge>
        <Badge variant="secondary" className="text-sm px-3 py-1">
          {totalMarks} Total Marks
        </Badge>
        {subjects.map((s) => (
          <Badge key={s} className="text-sm px-3 py-1 bg-primary/10 text-primary border-primary/20">
            {s}
          </Badge>
        ))}
        {exam?.date && (
          <span className="text-xs text-muted-foreground ml-auto">{exam.date}</span>
        )}
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {questionsLoading ? (
          [1, 2, 3].map((i) => <Skeleton key={i} className="h-32 rounded-lg" />)
        ) : questions?.length === 0 ? (
          <Card className="glass">
            <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
              <div className="rounded-2xl bg-primary/10 p-5">
                <BookOpen className="h-10 w-10 text-primary" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-lg">No questions yet</h3>
                <p className="text-muted-foreground text-sm mt-1">
                  Add your first question to this exam.
                </p>
              </div>
              <Button
                onClick={() => setBuilderOpen(true)}
                className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
              >
                <Plus className="mr-2 h-4 w-4" /> Add First Question
              </Button>
            </CardContent>
          </Card>
        ) : (
          questions?.map((q, index) => (
            <Card key={q.id} className="glass hover:-translate-y-0.5 hover:shadow-md transition-all duration-200">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    {/* Numbered indicator */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-xs font-bold text-primary">Q{index + 1}</span>
                    </div>
                    <CardTitle className="text-base font-heading leading-snug">
                      {q.question_text}
                    </CardTitle>
                  </div>
                  <Badge className="shrink-0">{q.marks} pts</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2 sm:grid-cols-2">
                  {q.choices?.map((c) => (
                    <div
                      key={c.id}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                        c.is_correct
                          ? "bg-gradient-to-r from-emerald-500/15 to-emerald-500/5 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30"
                          : "bg-muted/60"
                      }`}
                    >
                      {c.is_correct ? (
                        <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
                      ) : (
                        <span className="h-4 w-4 shrink-0 flex items-center justify-center rounded-full border-2 border-muted-foreground/30 text-[10px] font-semibold text-muted-foreground">
                          {c.label}
                        </span>
                      )}
                      <span className={c.is_correct ? "font-semibold" : ""}>{c.text}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <QuestionBuilder examId={id} open={builderOpen} onOpenChange={setBuilderOpen} />
    </div>
  );
}
