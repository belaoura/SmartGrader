import { CheckCircle2, XCircle, MinusCircle, Trophy, Target } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function ScanResults({ result }) {
  const pct = result.percentage || 0;
  const passed = pct >= 50;

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
                {result.obtained_marks}
                <span className="text-lg text-muted-foreground font-normal">/{result.total_marks}</span>
              </p>
              <p className="text-xs text-muted-foreground">Total Score</p>
            </div>
          </div>
          <div className="text-right">
            <Badge className={`text-lg px-4 py-1 font-bold border-0 ${passed ? "bg-emerald-500/15 text-emerald-600" : "bg-red-500/15 text-red-600"}`}>
              {pct}%
            </Badge>
            <p className="text-xs text-muted-foreground mt-1">{result.answered}/{result.total_questions} answered</p>
          </div>
        </div>
        {/* Progress bar */}
        <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${passed ? "bg-emerald-500" : "bg-red-500"}`}
            style={{ width: `${Math.min(pct, 100)}%` }}
          />
        </div>
      </div>

      {/* Question Breakdown */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-border flex items-center gap-2">
          <Target className="h-4 w-4 text-primary" />
          <h3 className="font-heading font-semibold text-sm">Question Breakdown</h3>
        </div>
        <div className="divide-y divide-border">
          {result.details?.map((d, idx) => (
            <div key={d.question_id} className={`flex items-center gap-4 px-5 py-3 ${
              d.is_correct ? "bg-emerald-500/[0.03]" : d.detected ? "bg-red-500/[0.03]" : ""
            }`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                d.is_correct ? "bg-emerald-500/15 text-emerald-600" :
                d.detected ? "bg-red-500/15 text-red-600" :
                "bg-amber-500/15 text-amber-600"
              }`}>
                {idx + 1}
              </div>
              <div className="flex-1 flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground w-16">Detected:</span>
                  <Badge variant="secondary" className="text-xs font-mono">{d.detected || "—"}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground w-14">Correct:</span>
                  <Badge className="text-xs font-mono bg-primary/10 text-primary border-0">{d.correct || "—"}</Badge>
                </div>
              </div>
              <div>
                {d.is_correct ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                ) : d.detected ? (
                  <XCircle className="h-5 w-5 text-red-500" />
                ) : (
                  <MinusCircle className="h-5 w-5 text-amber-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
