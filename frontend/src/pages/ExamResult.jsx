import { useParams, Link } from "react-router-dom";
import { CheckCircle2, XCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useExamResult } from "@/hooks/use-student-exam";

function ScoreBar({ score, maxScore }) {
  const pct = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
  const color =
    pct >= 75
      ? "bg-green-500"
      : pct >= 50
      ? "bg-yellow-500"
      : "bg-red-500";

  return (
    <div className="space-y-2">
      <div className="flex items-end justify-between">
        <div>
          <span className="text-4xl font-bold">{score}</span>
          <span className="text-lg text-muted-foreground ml-1">/ {maxScore}</span>
        </div>
        <span className="text-2xl font-semibold text-muted-foreground">{pct}%</span>
      </div>
      <div className="h-3 w-full rounded-full bg-muted overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function ExamResult() {
  const { sessionId } = useParams();
  const { data, isLoading, error } = useExamResult(sessionId);

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-2xl">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-32 rounded-xl" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-destructive">{error.message || "Failed to load result."}</p>
        <Button asChild variant="outline">
          <Link to="/exam"><ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard</Link>
        </Button>
      </div>
    );
  }

  const showResult = data?.show_result || "none";

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold">Exam Result</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {data?.exam_title || `Session #${sessionId}`}
          </p>
        </div>
        <Button asChild variant="outline">
          <Link to="/exam"><ArrowLeft className="mr-2 h-4 w-4" /> Dashboard</Link>
        </Button>
      </div>

      {showResult === "none" && (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <div className="rounded-2xl bg-muted p-5">
              <CheckCircle2 className="h-10 w-10 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Exam Submitted</h3>
              <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                Your answers have been saved. Results will be available later.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {(showResult === "score_only" || showResult === "score_and_answers") && (
        <Card className="glass">
          <CardHeader><CardTitle className="text-base">Your Score</CardTitle></CardHeader>
          <CardContent>
            <ScoreBar score={data?.score ?? 0} maxScore={data?.max_score ?? 1} />
          </CardContent>
        </Card>
      )}

      {showResult === "score_and_answers" && data?.questions && (
        <Card className="glass">
          <CardHeader><CardTitle className="text-base">Answer Review</CardTitle></CardHeader>
          <CardContent className="space-y-4 pt-0">
            {data.questions.map((q, idx) => (
              <div key={q.id} className="border border-border rounded-lg p-4 space-y-2">
                <div className="flex items-start gap-2">
                  {q.is_correct ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                  )}
                  <p className="text-sm font-medium leading-snug">
                    <span className="text-muted-foreground mr-1">{idx + 1}.</span>
                    {q.text}
                  </p>
                </div>
                <div className="pl-6 space-y-1 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <span>Your answer:</span>
                    <span className={q.is_correct ? "text-green-600 dark:text-green-400 font-medium" : "text-red-500 font-medium"}>
                      {q.selected_answer || "—"}
                    </span>
                  </div>
                  {!q.is_correct && (
                    <div className="flex items-center gap-2">
                      <span>Correct:</span>
                      <span className="text-green-600 dark:text-green-400 font-medium">{q.correct_answer || "—"}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
