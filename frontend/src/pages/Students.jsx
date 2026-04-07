import { useState } from "react";
import { Plus, Search, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { Pagination } from "@/components/ui/pagination";
import { useStudents } from "@/hooks/use-students";
import StudentList from "@/components/students/StudentList";
import StudentForm from "@/components/students/StudentForm";

const PAGE_SIZE = 5;

export default function Students() {
  const [formOpen, setFormOpen] = useState(false);
  const [editStudent, setEditStudent] = useState(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data: students, isLoading } = useStudents();

  const filtered = (students || []).filter((s) =>
    (s.name || "").toLowerCase().includes(search.toLowerCase()) ||
    (s.student_id || "").toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const isEmpty = !isLoading && (students || []).length === 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Students"
        description="Manage your student roster"
        helpText="Students are linked to exam results. Add students here before scanning their answer sheets."
      >
        <Button
          onClick={() => setFormOpen(true)}
          className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" /> Add Student
        </Button>
      </PageHeader>

      {/* Search + count */}
      {!isEmpty && (
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search by name or ID..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="pl-9 cursor-text"
            />
          </div>
          {!isLoading && (
            <Badge variant="secondary" className="shrink-0 text-sm px-3 py-1">
              {filtered.length} {filtered.length === 1 ? "student" : "students"}
            </Badge>
          )}
        </div>
      )}

      {/* Empty state */}
      {isEmpty ? (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <div className="rounded-2xl bg-emerald-500/10 p-5">
              <Users className="h-10 w-10 text-emerald-500" />
            </div>
            <div>
              <h3 className="font-heading font-semibold text-lg">No students yet</h3>
              <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                Add students to track their exam performance and results.
              </p>
            </div>
            <Button
              onClick={() => setFormOpen(true)}
              className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
            >
              <Plus className="mr-2 h-4 w-4" /> Add first student
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card className="glass">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="space-y-2 p-6">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 rounded" />
                ))}
              </div>
            ) : (
              <>
                <StudentList students={paginated} onEdit={(s) => { setEditStudent(s); setFormOpen(true); }} />
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                  pageSize={PAGE_SIZE}
                  totalItems={filtered.length}
                />
              </>
            )}
          </CardContent>
        </Card>
      )}

      <StudentForm
        open={formOpen}
        onOpenChange={(open) => { setFormOpen(open); if (!open) setEditStudent(null); }}
        student={editStudent}
      />
    </div>
  );
}
