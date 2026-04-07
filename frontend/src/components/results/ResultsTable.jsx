import { Badge } from "@/components/ui/badge";
import { Printer, TrendingUp, TrendingDown, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ResultsTable({ results }) {
  const handlePrint = (r) => {
    const win = window.open("", "_blank");
    win.document.write(`<!DOCTYPE html><html><head><title>Result - ${r.student_name}</title>
      <style>
        body { font-family: "Times New Roman", serif; font-size: 12pt; max-width: 21cm; margin: 0 auto; padding: 2cm; }
        h1 { font-size: 18pt; border-bottom: 2px solid #6366F1; padding-bottom: 8px; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #f5f3ff; font-weight: bold; }
        .pass { color: #10B981; font-weight: bold; } .fail { color: #EF4444; font-weight: bold; }
        @page { size: A4; margin: 2cm; }
      </style></head><body>
      <h1>Exam Result Certificate</h1>
      <table>
        <tr><th>Student</th><td>${r.student_name}</td></tr>
        <tr><th>Exam</th><td>${r.exam_title}</td></tr>
        <tr><th>Score</th><td>${r.score}</td></tr>
        <tr><th>Percentage</th><td class="${r.percentage >= 50 ? 'pass' : 'fail'}">${r.percentage?.toFixed(1)}%</td></tr>
        <tr><th>Status</th><td class="${r.percentage >= 50 ? 'pass' : 'fail'}">${r.percentage >= 50 ? 'PASS' : 'FAIL'}</td></tr>
        <tr><th>Graded At</th><td>${r.graded_at || '-'}</td></tr>
      </table>
    </body></html>`);
    win.document.close();
    win.onload = () => win.print();
  };

  if (results.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-12 px-6">
        No results found.
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {results.map((r, idx) => {
        const passed = (r.percentage || 0) >= 50;
        return (
          <div
            key={r.id}
            className="group flex items-center gap-4 px-5 py-4 hover:bg-accent/40 transition-all duration-200"
          >
            {/* Rank/Index */}
            <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${
              passed ? "bg-emerald-500/10" : "bg-red-500/10"
            }`}>
              <span className={`text-sm font-bold ${passed ? "text-emerald-600" : "text-red-500"}`}>
                {idx + 1}
              </span>
            </div>

            {/* Student + Exam info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <h4 className="font-heading font-semibold text-sm truncate">{r.student_name}</h4>
              </div>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="truncate">{r.exam_title}</span>
                {r.graded_at && (
                  <span className="flex items-center gap-1 shrink-0">
                    <Clock className="h-3 w-3" />
                    {r.graded_at}
                  </span>
                )}
              </div>
            </div>

            {/* Score */}
            <div className="hidden sm:flex flex-col items-end gap-0.5">
              <span className="text-sm font-bold font-heading">{r.score}</span>
              <span className="text-[10px] text-muted-foreground">score</span>
            </div>

            {/* Percentage badge */}
            <Badge
              className={`text-xs px-3 py-1 font-semibold border-0 gap-1 ${
                passed
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                  : "bg-red-500/10 text-red-600 dark:text-red-400"
              }`}
            >
              {passed ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {r.percentage?.toFixed(1)}%
            </Badge>

            {/* Print action */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              title="Print result"
              onClick={() => handlePrint(r)}
            >
              <Printer className="h-3.5 w-3.5 text-muted-foreground" />
            </Button>
          </div>
        );
      })}
    </div>
  );
}
