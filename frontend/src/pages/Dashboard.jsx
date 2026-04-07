import { Link } from "react-router-dom";
import { FileText, HelpCircle, Users, TrendingUp, ArrowRight, Sparkles } from "lucide-react";
import { useExams } from "@/hooks/use-exams";
import { useStudents } from "@/hooks/use-students";
import StatCard from "@/components/dashboard/StatCard";
import { ResultsBarChart, PassFailPieChart } from "@/components/dashboard/Charts";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const { data: exams, isLoading: examsLoading } = useExams();
  const { data: students, isLoading: studentsLoading } = useStudents();

  const isLoading = examsLoading || studentsLoading;

  const totalExams = exams?.length || 0;
  const totalQuestions =
    exams?.reduce((sum, e) => sum + (e.statistics?.question_count || 0), 0) || 0;
  const totalStudents = students?.length || 0;
  const avgScore = exams?.length
    ? (
        exams.reduce((sum, e) => sum + (e.statistics?.average_score || 0), 0) / exams.length
      ).toFixed(1)
    : "0";

  const barData = (exams || []).map((e) => ({
    name: e.title?.substring(0, 15) || "Untitled",
    average: e.statistics?.average_score || 0,
  }));

  // Sample pass/fail data — will be computed from real results when available
  const pieData = [
    { name: "Pass", value: 65 },
    { name: "Fail", value: 35 },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-16 rounded-lg" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-72 rounded-lg" />
          <Skeleton className="h-72 rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Overview of your exam management system"
        helpText="The dashboard shows real-time statistics about your exams, students, and grading results."
      />

      {/* Welcome banner */}
      <div className="glass rounded-xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-primary/10 p-3 shrink-0">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h3 className="font-heading font-semibold text-lg leading-tight">
              Welcome to SmartGrader
            </h3>
            <p className="text-sm text-muted-foreground mt-0.5 max-w-lg">
              Create and manage multiple-choice exams, generate printable answer sheets, scan filled
              sheets with computer vision, and grade short answers using AI.
            </p>
          </div>
        </div>
        <Link to="/help" className="shrink-0">
          <Button variant="outline" className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200 gap-2">
            Get Started
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={FileText} label="Total Exams" value={totalExams} color="indigo" />
        <StatCard icon={HelpCircle} label="Total Questions" value={totalQuestions} color="violet" />
        <StatCard icon={Users} label="Total Students" value={totalStudents} color="emerald" />
        <StatCard icon={TrendingUp} label="Avg Score" value={`${avgScore}%`} color="amber" />
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ResultsBarChart data={barData} />
        <PassFailPieChart data={pieData} />
      </div>
    </div>
  );
}
