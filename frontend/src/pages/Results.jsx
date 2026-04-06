import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useExams } from "@/hooks/use-exams";
import { useExamResults } from "@/hooks/use-results";
import ResultsTable from "@/components/results/ResultsTable";
import ExportButton from "@/components/results/ExportButton";

export default function Results() {
  const [selectedExam, setSelectedExam] = useState("");
  const { data: exams } = useExams();
  const { data: results, isLoading } = useExamResults(selectedExam || undefined);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-heading">Results</h2>
        <ExportButton results={results || []} />
      </div>

      <div className="max-w-xs">
        <Select value={selectedExam} onValueChange={setSelectedExam}>
          <SelectTrigger className="cursor-pointer">
            <SelectValue placeholder="Filter by exam..." />
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

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 rounded" />)}
            </div>
          ) : (
            <ResultsTable results={results || []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
