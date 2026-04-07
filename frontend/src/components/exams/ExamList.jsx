import { useNavigate } from "react-router-dom";
import { Trash2, Printer, ChevronRight, Calendar, HelpCircle, Award } from "lucide-react";
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

  const handlePrint = (e, exam) => {
    e.stopPropagation();
    navigate(`/exams/${exam.id}`);
  };

  if (exams.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-12 px-6">
        No exams match your search.
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {exams.map((exam, idx) => (
        <div
          key={exam.id}
          className="group flex items-center gap-4 px-5 py-4 cursor-pointer hover:bg-accent/40 transition-all duration-200"
          onClick={() => navigate(`/exams/${exam.id}`)}
        >
          {/* Index number */}
          <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
            <span className="text-sm font-bold text-primary">{idx + 1}</span>
          </div>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <h4 className="font-heading font-semibold text-sm truncate">{exam.title}</h4>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {exam.subject && (
                <span className="flex items-center gap-1">
                  <Award className="h-3 w-3" />
                  {exam.subject}
                </span>
              )}
              {exam.date && (
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {exam.date}
                </span>
              )}
            </div>
          </div>

          {/* Stats badges */}
          <div className="hidden sm:flex items-center gap-2">
            <Badge variant="secondary" className="text-xs px-2.5 py-0.5 gap-1">
              <HelpCircle className="h-3 w-3" />
              {exam.statistics?.question_count || 0} Q
            </Badge>
            <Badge className="text-xs px-2.5 py-0.5 bg-primary/10 text-primary border-0">
              {exam.total_marks || 0} pts
            </Badge>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer"
              title="Open & Print"
              onClick={(e) => handlePrint(e, exam)}
            >
              <Printer className="h-3.5 w-3.5 text-muted-foreground" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 cursor-pointer hover:text-destructive"
              title="Delete exam"
              onClick={(e) => handleDelete(e, exam.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>

          {/* Chevron */}
          <ChevronRight className="h-4 w-4 text-muted-foreground/40 group-hover:text-primary group-hover:translate-x-0.5 transition-all duration-200 shrink-0" />
        </div>
      ))}
    </div>
  );
}
