import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useExams } from "@/hooks/use-exams";
import ExamList from "@/components/exams/ExamList";
import ExamForm from "@/components/exams/ExamForm";

export default function Exams() {
  const [formOpen, setFormOpen] = useState(false);
  const { data: exams, isLoading } = useExams();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-heading">Exams</h2>
        <Button onClick={() => setFormOpen(true)} className="cursor-pointer">
          <Plus className="mr-2 h-4 w-4" /> New Exam
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-12 rounded" />
              ))}
            </div>
          ) : (
            <ExamList exams={exams || []} />
          )}
        </CardContent>
      </Card>

      <ExamForm open={formOpen} onOpenChange={setFormOpen} />
    </div>
  );
}
