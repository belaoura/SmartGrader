import { Link } from "react-router-dom";
import { Plus, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { useSessions } from "@/hooks/use-sessions";

function statusBadge(status) {
  switch (status) {
    case "active":
      return <Badge className="bg-green-500/15 text-green-600 dark:text-green-400 border-green-500/30">Active</Badge>;
    case "scheduled":
      return <Badge className="bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30">Scheduled</Badge>;
    case "ended":
    default:
      return <Badge variant="secondary">Ended</Badge>;
  }
}

function formatDt(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function ExamSessions() {
  const { data: sessions, isLoading } = useSessions();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Online Exam Sessions"
        description="Create and monitor online exam sessions for your students"
      >
        <Button asChild className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200">
          <Link to="/sessions/new">
            <Plus className="mr-2 h-4 w-4" /> New Session
          </Link>
        </Button>
      </PageHeader>

      <Card className="glass">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-14 rounded" />)}
            </div>
          ) : !sessions || sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
              <div className="rounded-2xl bg-primary/10 p-5">
                <Monitor className="h-10 w-10 text-primary" />
              </div>
              <div>
                <h3 className="font-heading font-semibold text-lg">No sessions yet</h3>
                <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                  Create a session to let students take exams online with live monitoring.
                </p>
              </div>
              <Button asChild className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200">
                <Link to="/sessions/new">
                  <Plus className="mr-2 h-4 w-4" /> Create first session
                </Link>
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {sessions.map((session) => (
                <Link
                  key={session.id}
                  to={`/sessions/${session.id}`}
                  className="flex items-center justify-between px-6 py-4 hover:bg-accent/50 transition-colors group"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="font-medium truncate">{session.exam_title || session.exam?.title || `Session #${session.id}`}</span>
                      {statusBadge(session.status)}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Start: {formatDt(session.start_time)}</span>
                      <span>End: {formatDt(session.end_time)}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    <Badge variant="secondary">{session.assignment_count ?? 0} assigned</Badge>
                    <ChevronRightIcon />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function ChevronRightIcon() {
  return (
    <svg className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}
