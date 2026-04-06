import { useNavigate } from "react-router-dom";
import { Pencil, Trash2 } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDeleteExam } from "@/hooks/use-exams";

export default function ExamList({ exams }) {
  const navigate = useNavigate();
  const deleteExam = useDeleteExam();

  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (window.confirm("Delete this exam and all its questions?")) {
      deleteExam.mutate(id);
    }
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Subject</TableHead>
          <TableHead>Date</TableHead>
          <TableHead className="text-center">Questions</TableHead>
          <TableHead className="text-center">Total Marks</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {exams.map((exam) => (
          <TableRow
            key={exam.id}
            className="cursor-pointer hover:bg-accent/50 transition-colors"
            onClick={() => navigate(`/exams/${exam.id}`)}
          >
            <TableCell className="font-medium">{exam.title}</TableCell>
            <TableCell>{exam.subject || "-"}</TableCell>
            <TableCell>{exam.date || "-"}</TableCell>
            <TableCell className="text-center">
              <Badge variant="secondary">{exam.statistics?.question_count || 0}</Badge>
            </TableCell>
            <TableCell className="text-center">{exam.total_marks || "-"}</TableCell>
            <TableCell className="text-right">
              <Button
                variant="ghost"
                size="icon"
                className="cursor-pointer"
                onClick={(e) => handleDelete(e, exam.id)}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
        {exams.length === 0 && (
          <TableRow>
            <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
              No exams yet. Create your first exam!
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
