import { useState } from "react";
import { CheckCircle2, AlertTriangle, Edit3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
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

  return (
    <div className="space-y-4">
      <Card className="border-primary/20">
        <CardContent className="flex items-center justify-center gap-6 p-8">
          <div className="text-center">
            <p className="text-4xl font-bold font-heading text-primary">
              {totalScore}/{totalMax}
            </p>
            <p className="text-lg text-muted-foreground">
              {totalMax > 0 ? ((totalScore / totalMax) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-base">AI Grading Results</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Question</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Feedback</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {grades.map((g) => (
                <TableRow
                  key={g.question_id}
                  className={g.needs_review ? "bg-amber-500/5" : ""}
                >
                  <TableCell>Q{g.question_id}</TableCell>
                  <TableCell>
                    {g.score}/{g.max}
                  </TableCell>
                  <TableCell className="max-w-xs truncate text-sm">
                    {g.feedback}
                  </TableCell>
                  <TableCell>
                    {g.needs_review ? (
                      <Badge variant="outline" className="border-amber-500 text-amber-500">
                        <AlertTriangle className="mr-1 h-3 w-3" />
                        {(g.confidence * 100).toFixed(0)}%
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-green-500 text-green-500">
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                        {(g.confidence * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openCorrection(g)}
                      className="cursor-pointer"
                    >
                      <Edit3 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={!!correcting} onOpenChange={(open) => !open && setCorrecting(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-heading">Correct Grade - Q{correcting?.question_id}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              AI gave: {correcting?.score}/{correcting?.max} ({correcting?.feedback})
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
