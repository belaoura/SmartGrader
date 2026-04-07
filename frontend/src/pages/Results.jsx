import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/ui/page-header";
import { HelpTooltip } from "@/components/ui/help-tooltip";
import { Pagination } from "@/components/ui/pagination";
import { useExams } from "@/hooks/use-exams";
import { useExamResults } from "@/hooks/use-results";
import ResultsTable from "@/components/results/ResultsTable";
import ExportButton from "@/components/results/ExportButton";
import { BarChart2, Users, TrendingUp, ClipboardList } from "lucide-react";

const PAGE_SIZE = 5;

function SummaryCard({ icon: Icon, label, value, color = "indigo" }) {
  const colorMap = {
    indigo: { bg: "bg-indigo-500/10", text: "text-indigo-500" },
    emerald: { bg: "bg-emerald-500/10", text: "text-emerald-500" },
    amber: { bg: "bg-amber-500/10", text: "text-amber-500" },
    violet: { bg: "bg-violet-500/10", text: "text-violet-500" },
  };
  const c = colorMap[color] || colorMap.indigo;
  return (
    <div className="glass rounded-xl p-4 flex items-center gap-3 hover:-translate-y-0.5 hover:shadow-md transition-all duration-200 cursor-default">
      <div className={`rounded-lg ${c.bg} p-2.5 shrink-0`}>
        <Icon className={`h-5 w-5 ${c.text}`} />
      </div>
      <div>
        <p className="text-2xl font-extrabold font-heading leading-none">{value}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
      </div>
    </div>
  );
}

export default function Results() {
  const [selectedExam, setSelectedExam] = useState("");
  const [page, setPage] = useState(1);
  const { data: exams } = useExams();
  const { data: results, isLoading } = useExamResults(selectedExam || undefined);

  // Compute summary stats
  const totalResults = results?.length || 0;
  const avgScore = totalResults
    ? (results.reduce((s, r) => s + (r.percentage || 0), 0) / totalResults).toFixed(1)
    : "—";
  const passRate = totalResults
    ? `${Math.round((results.filter((r) => (r.percentage || 0) >= 50).length / totalResults) * 100)}%`
    : "—";

  const totalPages = Math.ceil(totalResults / PAGE_SIZE);
  const paginated = (results || []).slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const noExamSelected = !selectedExam;
  const noResults = !isLoading && selectedExam && totalResults === 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Results"
        description="View and export graded exam results"
        helpText="Results are generated after scanning an answer sheet. Select an exam to view all results for that exam."
      >
        <ExportButton results={results || []} />
      </PageHeader>

      {/* Exam filter */}
      <div className="glass rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="flex items-center gap-2">
          <Label className="text-sm font-medium whitespace-nowrap">Filter by Exam</Label>
          <HelpTooltip text="Select an exam to see all graded results for that exam." />
        </div>
        <Select value={selectedExam} onValueChange={(v) => { setSelectedExam(v); setPage(1); }}>
          <SelectTrigger className="cursor-pointer w-full sm:w-72">
            <SelectValue placeholder="Choose an exam to view results..." />
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

      {/* Summary stats (only when exam selected and has results) */}
      {selectedExam && !isLoading && totalResults > 0 && (
        <div className="grid gap-3 sm:grid-cols-3">
          <SummaryCard icon={ClipboardList} label="Total Results" value={totalResults} color="indigo" />
          <SummaryCard icon={BarChart2} label="Average Score" value={`${avgScore}%`} color="amber" />
          <SummaryCard icon={TrendingUp} label="Pass Rate" value={passRate} color="emerald" />
        </div>
      )}

      {/* Results table or empty states */}
      {noExamSelected ? (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <div className="rounded-2xl bg-primary/10 p-5">
              <BarChart2 className="h-10 w-10 text-primary" />
            </div>
            <div>
              <h3 className="font-heading font-semibold text-lg">Select an Exam</h3>
              <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                Choose an exam from the dropdown above to view its graded results.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : noResults ? (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <div className="rounded-2xl bg-muted p-5">
              <Users className="h-10 w-10 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-heading font-semibold text-lg">No results yet</h3>
              <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                No graded results found for this exam. Use the Scanner to grade answer sheets.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="glass">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="space-y-2 p-6">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 rounded" />
                ))}
              </div>
            ) : (
              <>
                <ResultsTable results={paginated} />
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                  pageSize={PAGE_SIZE}
                  totalItems={totalResults}
                />
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
