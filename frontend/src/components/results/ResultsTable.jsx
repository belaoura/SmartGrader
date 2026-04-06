import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function ResultsTable({ results }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Student</TableHead>
          <TableHead>Exam</TableHead>
          <TableHead className="text-center">Score</TableHead>
          <TableHead className="text-center">Percentage</TableHead>
          <TableHead>Graded At</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {results.map((r) => (
          <TableRow key={r.id} className="hover:bg-accent/50 transition-colors">
            <TableCell className="font-medium">{r.student_name}</TableCell>
            <TableCell>{r.exam_title}</TableCell>
            <TableCell className="text-center">{r.score}</TableCell>
            <TableCell className="text-center">
              <Badge variant={r.percentage >= 50 ? "default" : "destructive"}>
                {r.percentage?.toFixed(1)}%
              </Badge>
            </TableCell>
            <TableCell className="text-muted-foreground">{r.graded_at || "-"}</TableCell>
          </TableRow>
        ))}
        {results.length === 0 && (
          <TableRow>
            <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
              No results yet.
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
