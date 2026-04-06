import { FileText, HelpCircle, Users, TrendingUp } from "lucide-react";
import { useExams } from "@/hooks/use-exams";
import { useStudents } from "@/hooks/use-students";
import StatCard from "@/components/dashboard/StatCard";
import { ResultsBarChart, PassFailPieChart } from "@/components/dashboard/Charts";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const { data: exams, isLoading: examsLoading } = useExams();
  const { data: students, isLoading: studentsLoading } = useStudents();

  const isLoading = examsLoading || studentsLoading;

  const totalExams = exams?.length || 0;
  const totalQuestions = exams?.reduce((sum, e) => sum + (e.statistics?.question_count || 0), 0) || 0;
  const totalStudents = students?.length || 0;
  const avgScore = exams?.length
    ? (exams.reduce((sum, e) => sum + (e.statistics?.average_score || 0), 0) / exams.length).toFixed(1)
    : "0";

  const barData = (exams || []).map((e) => ({
    name: e.title?.substring(0, 15) || "Untitled",
    average: e.statistics?.average_score || 0,
  }));

  const pieData = [
    { name: "Pass", value: 65 },
    { name: "Fail", value: 35 },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold font-heading">Dashboard</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold font-heading">Dashboard</h2>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={FileText} label="Total Exams" value={totalExams} />
        <StatCard icon={HelpCircle} label="Total Questions" value={totalQuestions} />
        <StatCard icon={Users} label="Total Students" value={totalStudents} />
        <StatCard icon={TrendingUp} label="Avg Score" value={`${avgScore}%`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ResultsBarChart data={barData} />
        <PassFailPieChart data={pieData} />
      </div>
    </div>
  );
}
