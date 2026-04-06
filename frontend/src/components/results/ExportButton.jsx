import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ExportButton({ results, filename = "results" }) {
  const handleExport = () => {
    const headers = ["Student", "Exam", "Score", "Percentage", "Graded At"];
    const rows = results.map((r) => [
      r.student_name, r.exam_title, r.score, r.percentage?.toFixed(1), r.graded_at || "",
    ]);
    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Button variant="outline" onClick={handleExport} disabled={!results?.length} className="cursor-pointer">
      <Download className="mr-2 h-4 w-4" /> Export CSV
    </Button>
  );
}
