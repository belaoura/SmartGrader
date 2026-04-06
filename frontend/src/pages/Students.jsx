import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useStudents } from "@/hooks/use-students";
import StudentList from "@/components/students/StudentList";
import StudentForm from "@/components/students/StudentForm";

export default function Students() {
  const [formOpen, setFormOpen] = useState(false);
  const { data: students, isLoading } = useStudents();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-heading">Students</h2>
        <Button onClick={() => setFormOpen(true)} className="cursor-pointer">
          <Plus className="mr-2 h-4 w-4" /> Add Student
        </Button>
      </div>
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 rounded" />)}
            </div>
          ) : (
            <StudentList students={students || []} />
          )}
        </CardContent>
      </Card>
      <StudentForm open={formOpen} onOpenChange={setFormOpen} />
    </div>
  );
}
