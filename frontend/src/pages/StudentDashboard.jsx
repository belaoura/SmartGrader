import { Link } from "react-router-dom";
import { Clock, CheckCircle2, PlayCircle, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useStudentExams } from "@/hooks/use-student-exam";

function formatDt(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function ExamCard({ exam, type }) {
  return (
    <Card className="glass hover:shadow-md transition-shadow">
      <CardContent className="pt-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-medium leading-tight">{exam.exam_title || exam.title || `Exam #${exam.session_id}`}</h3>
          {type === "active" && (
            <Badge className="bg-green-500/15 text-green-600 dark:text-green-400 border-green-500/30 shrink-0">Active</Badge>
          )}
          {type === "upcoming" && (
            <Badge className="bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30 shrink-0">Upcoming</Badge>
          )}
          {type === "completed" && (
            <Badge variant="secondary" className="shrink-0">Completed</Badge>
          )}
        </div>

        <div className="text-xs text-muted-foreground space-y-1">
          {exam.start_time && <p>Start: {formatDt(exam.start_time)}</p>}
          {exam.end_time && <p>End: {formatDt(exam.end_time)}</p>}
        </div>

        {type === "completed" && exam.score != null && (
          <div className="flex items-center gap-2 text-sm">
            <span className="font-semibold text-primary">{exam.score}</span>
            {exam.max_score != null && (
              <span className="text-muted-foreground">/ {exam.max_score}</span>
            )}
            {exam.percentage != null && (
              <span className="text-muted-foreground">({exam.percentage}%)</span>
            )}
          </div>
        )}

        <div className="pt-1">
          {type === "active" && (
            <Button asChild size="sm" className="w-full cursor-pointer hover:-translate-y-0.5 transition-all duration-200">
              <Link to={`/exam/${exam.session_id}`}>
                <PlayCircle className="mr-2 h-4 w-4" />
                {exam.attempt_status === "in_progress" ? "Resume Exam" : "Start Exam"}
              </Link>
            </Button>
          )}
          {type === "upcoming" && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              Not yet available
            </div>
          )}
          {type === "completed" && (
            <Button asChild variant="outline" size="sm" className="w-full cursor-pointer">
              <Link to={`/exam/${exam.session_id}/result`}>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                View Result
              </Link>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function Section({ title, icon: Icon, exams, type, emptyText }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Icon className="h-5 w-5 text-muted-foreground" />
        <h2 className="font-heading font-semibold text-lg">{title}</h2>
        <Badge variant="secondary">{exams.length}</Badge>
      </div>
      {exams.length === 0 ? (
        <p className="text-sm text-muted-foreground">{emptyText}</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {exams.map((exam) => (
            <ExamCard key={exam.session_id} exam={exam} type={type} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function StudentDashboard() {
  const { data, isLoading } = useStudentExams();

  const upcoming = data?.upcoming || [];
  const active = data?.active || [];
  const completed = data?.completed || [];

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-40 rounded-xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-10 max-w-5xl">
      <div>
        <h1 className="text-2xl font-heading font-bold">My Exams</h1>
        <p className="text-muted-foreground text-sm mt-1">View and take your assigned exams</p>
      </div>

      <Section
        title="Active"
        icon={PlayCircle}
        exams={active}
        type="active"
        emptyText="No active exams right now."
      />

      <Section
        title="Upcoming"
        icon={Calendar}
        exams={upcoming}
        type="upcoming"
        emptyText="No upcoming exams scheduled."
      />

      <Section
        title="Completed"
        icon={CheckCircle2}
        exams={completed}
        type="completed"
        emptyText="You haven't completed any exams yet."
      />
    </div>
  );
}
