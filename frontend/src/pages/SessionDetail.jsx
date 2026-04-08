import { useParams, Link } from "react-router-dom";
import { ArrowLeft, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { useSession, useMonitorSession } from "@/hooks/use-sessions";

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

function attemptStatusBadge(status) {
  switch (status) {
    case "submitted":
      return <Badge className="bg-green-500/15 text-green-600 dark:text-green-400 border-green-500/30">Submitted</Badge>;
    case "in_progress":
      return <Badge className="bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30">In Progress</Badge>;
    case "not_started":
    default:
      return <Badge variant="outline">Not Started</Badge>;
  }
}

function formatDt(dt) {
  if (!dt) return "—";
  return new Date(dt).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export default function SessionDetail() {
  const { id } = useParams();
  const { data: session, isLoading: loadingSession } = useSession(id);
  const { data: monitor, isLoading: loadingMonitor, dataUpdatedAt } = useMonitorSession(id, !!session);

  const students = monitor?.students || [];
  const total = monitor?.total ?? 0;
  const started = monitor?.started ?? 0;
  const submitted = monitor?.submitted ?? 0;

  if (loadingSession) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 rounded-xl" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        Session not found.{" "}
        <Link to="/sessions" className="text-primary hover:underline">Back to sessions</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={session.exam_title || session.exam?.title || `Session #${session.id}`}
        description={`Created ${formatDt(session.created_at)}`}
      >
        <Button asChild variant="outline" size="sm">
          <Link to="/sessions"><ArrowLeft className="mr-2 h-4 w-4" /> Back</Link>
        </Button>
      </PageHeader>

      {/* Session info */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Status</p>
            <div>{statusBadge(session.status)}</div>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Start</p>
            <p className="text-sm font-medium">{formatDt(session.start_time)}</p>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">End</p>
            <p className="text-sm font-medium">{formatDt(session.end_time)}</p>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Display Mode</p>
            <p className="text-sm font-medium capitalize">{(session.display_mode || "").replace(/_/g, " ")}</p>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Save Mode</p>
            <p className="text-sm font-medium capitalize">{(session.save_mode || "").replace(/_/g, " ")}</p>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="pt-4 space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Show Result</p>
            <p className="text-sm font-medium capitalize">{(session.show_result || "none").replace(/_/g, " ")}</p>
          </CardContent>
        </Card>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Assigned", value: total, color: "text-foreground" },
          { label: "Started", value: started, color: "text-blue-500" },
          { label: "Submitted", value: submitted, color: "text-green-500" },
        ].map(({ label, value, color }) => (
          <Card key={label} className="glass">
            <CardContent className="pt-4 text-center">
              <p className={`text-3xl font-bold ${color}`}>{value}</p>
              <p className="text-xs text-muted-foreground mt-1">{label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Live monitor table */}
      <Card className="glass">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Live Monitor</CardTitle>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <RefreshCw className="h-3.5 w-3.5 animate-spin-slow" />
            Auto-refreshes every 10s
            {dataUpdatedAt > 0 && (
              <span>· Updated {new Date(dataUpdatedAt).toLocaleTimeString()}</span>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loadingMonitor && students.length === 0 ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10 rounded" />)}
            </div>
          ) : students.length === 0 ? (
            <div className="py-10 text-center text-muted-foreground text-sm">
              No students assigned to this session yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left px-4 py-2 font-medium text-muted-foreground">Student</th>
                    <th className="text-left px-4 py-2 font-medium text-muted-foreground">Matricule</th>
                    <th className="text-left px-4 py-2 font-medium text-muted-foreground">Status</th>
                    <th className="text-center px-4 py-2 font-medium text-muted-foreground">Answers</th>
                    <th className="text-center px-4 py-2 font-medium text-muted-foreground">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {students.map((s) => (
                    <tr key={s.id} className="hover:bg-accent/30 transition-colors">
                      <td className="px-4 py-2.5 font-medium">{s.name}</td>
                      <td className="px-4 py-2.5 text-muted-foreground">{s.student_id || s.matricule || "—"}</td>
                      <td className="px-4 py-2.5">{attemptStatusBadge(s.status)}</td>
                      <td className="px-4 py-2.5 text-center">{s.answers_count ?? "—"}</td>
                      <td className="px-4 py-2.5 text-center">
                        {s.score != null ? (
                          <span className="font-medium">{s.score}</span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
