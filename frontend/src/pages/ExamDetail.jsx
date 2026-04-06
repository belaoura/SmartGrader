import { useState } from "react";
import { useParams } from "react-router-dom";
import { Plus, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useExam, useExamQuestions } from "@/hooks/use-exams";
import QuestionBuilder from "@/components/exams/QuestionBuilder";

export default function ExamDetail() {
  const { id } = useParams();
  const [builderOpen, setBuilderOpen] = useState(false);
  const { data: exam, isLoading: examLoading } = useExam(id);
  const { data: questions, isLoading: questionsLoading } = useExamQuestions(id);

  if (examLoading) {
    return <Skeleton className="h-64 rounded-lg" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold font-heading">{exam?.title}</h2>
          <p className="text-muted-foreground">
            {exam?.subject} {exam?.date && `| ${exam.date}`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setBuilderOpen(true)} className="cursor-pointer">
            <Plus className="mr-2 h-4 w-4" /> Add Question
          </Button>
        </div>
      </div>

      <div className="flex gap-3">
        <Badge variant="secondary">
          {exam?.statistics?.question_count || 0} Questions
        </Badge>
        <Badge variant="secondary">
          {exam?.statistics?.total_marks || 0} Total Marks
        </Badge>
      </div>

      <div className="space-y-4">
        {questionsLoading ? (
          [1, 2, 3].map((i) => <Skeleton key={i} className="h-32 rounded-lg" />)
        ) : questions?.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No questions yet. Add your first question!
            </CardContent>
          </Card>
        ) : (
          questions?.map((q, index) => (
            <Card key={q.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base font-heading">
                    Q{index + 1}. {q.question_text}
                  </CardTitle>
                  <Badge>{q.marks} pts</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2 sm:grid-cols-2">
                  {q.choices?.map((c) => (
                    <div
                      key={c.id}
                      className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm ${
                        c.is_correct
                          ? "bg-green-500/10 text-green-700 dark:text-green-400"
                          : "bg-muted"
                      }`}
                    >
                      {c.is_correct && <CheckCircle2 className="h-4 w-4 shrink-0" />}
                      <span className="font-medium">{c.label}.</span>
                      <span>{c.text}</span>
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
