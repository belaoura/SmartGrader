import { useState } from "react";
import { CheckCircle2, AlertTriangle, Edit3, Trophy, Brain } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCorrect } from "@/hooks/use-ai";

export default function AIGradeResults({ grades, answers }) {
  const [correcting, setCorrecting] = useState(null);
  const [teacherScore, setTeacherScore] = useState("");
  const [teacherFeedback, setTeacherFeedback] = useState("");
  const correctMutation = useCorrect();

  const openCorrection = (grade) => {
    setCorrecting(grade);
    setTeacherScore(String(grade.score));
    setTeacherFeedback("");
  };

  const submitCorrection = () => {
    if (!correcting) return;
    const answer = answers.find((a) => a.question_id === correcting.question_id);
    correctMutation.mutate(
      {
        question_id: correcting.question_id,
        student_text: answer?.text || "",
        ai_score: correcting.score,
        ai_feedback: correcting.feedback,
        teacher_score: parseFloat(teacherScore),
        teacher_feedback: teacherFeedback,
      },
      { onSuccess: () => setCorrecting(null) }
    );
  };

  const totalScore = grades.reduce((s, g) => s + g.score, 0);
  const totalMax = grades.reduce((s, g) => s + g.max, 0);
  const pct = totalMax > 0 ? ((totalScore / totalMax) * 100).toFixed(1) : 0;
  const passed = parseFloat(pct) >= 50;

  return (
    <div className="space-y-4">
      {/* Score Hero Card */}
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${passed ? "bg-emerald-500/15" : "bg-red-500/15"}`}>
              <Trophy className={`h-6 w-6 ${passed ? "text-emerald-500" : "text-red-500"}`} />
            </div>
            <div>
              <p className="text-3xl font-extrabold font-heading">
                {totalScore}
                <span className="text-lg text-muted-foreground font-normal">/{totalMax}</span>
              </p>
              <p className="text-xs text-muted-foreground">AI Total Score</p>
            </div>
          </div>
          <div className="text-right">
            <Badge className={`text-lg px-4 py-1 font-bold border-0 ${passed ? "bg-emerald-500/15 text-emerald-600" : "bg-red-500/15 text-red-600"}`}>
              {pct}%
            </Badge>
            <p className="text-xs text-muted-foreground mt-1">{grades.length} questions graded</p>
          </div>
        </div>
        {/* Progress bar */}
        <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${passed ? "bg-emerald-500" : "bg-red-500"}`}
            style={{ width: `${Math.min(parseFloat(pct), 100)}%` }}
          />
        </div>
      </div>

      {/* Grade Rows */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-border flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary" />
          <h3 className="font-heading font-semibold text-sm">AI Grading Results</h3>
        </div>
        <div className="divide-y divide-border">
          {grades.map((g, idx) => (
            <div
              key={g.question_id}
              className={`flex items-start gap-4 px-5 py-4 ${g.needs_review ? "bg-amber-500/[0.03]" : ""}`}
            >
              {/* Question number */}
              <div className={`w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-xs font-bold ${
                g.needs_review ? "bg-amber-500/15 text-amber-600" : "bg-primary/10 text-primary"
              }`}>
                {idx + 1}
              </div>

              {/* Score + feedback */}
              <div className="flex-1 min-w-0 space-y-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-sm font-semibold font-heading">
                    {g.score}<span className="text-muted-foreground font-normal">/{g.max}</span>
                  </span>
                  {g.needs_review ? (
                    <Badge variant="outline" className="border-amber-500/50 text-amber-600 text-xs">
                      <AlertTriangle className="mr-1 h-3 w-3" />
                      {(g.confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 text-xs">
                      <CheckCircle2 className="mr-1 h-3 w-3" />
                      {(g.confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">{g.feedback}</p>
              </div>

              {/* Edit button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => openCorrection(g)}
                className="cursor-pointer shrink-0 h-8 w-8 p-0 hover:bg-primary/10 hover:text-primary"
              >
                <Edit3 className="h-3.5 w-3.5" />
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Correction Dialog */}
      <Dialog open={!!correcting} onOpenChange={(open) => !open && setCorrecting(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-heading">Correct Grade — Q{correcting?.question_id}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              AI gave: {correcting?.score}/{correcting?.max} — {correcting?.feedback}
            </p>
            <div className="space-y-2">
              <Label htmlFor="t-score">Correct Score</Label>
              <Input
                id="t-score"
                type="number"
                min="0"
                max={correcting?.max}
                step="0.5"
                value={teacherScore}
                onChange={(e) => setTeacherScore(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="t-feedback">Feedback (optional)</Label>
              <Input
                id="t-feedback"
                value={teacherFeedback}
                onChange={(e) => setTeacherFeedback(e.target.value)}
                placeholder="Why this score?"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={submitCorrection}
              disabled={correctMutation.isPending}
              className="cursor-pointer"
            >
              {correctMutation.isPending ? "Saving..." : "Save Correction"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
