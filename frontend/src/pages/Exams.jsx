import { useState } from "react";
import { Plus, Search, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/ui/page-header";
import { Pagination } from "@/components/ui/pagination";
import { useExams } from "@/hooks/use-exams";
import ExamList from "@/components/exams/ExamList";
import ExamForm from "@/components/exams/ExamForm";

const PAGE_SIZE = 8;

export default function Exams() {
  const [formOpen, setFormOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data: exams, isLoading } = useExams();

  const filtered = (exams || []).filter((e) =>
    (e.title || "").toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const isEmpty = !isLoading && (exams || []).length === 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Exams"
        description="Create and manage your multiple-choice exams"
        helpText="Exams contain questions and choices. Each exam can be printed as an answer sheet and scanned for automatic grading."
      >
        <Button onClick={() => setFormOpen(true)} className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200">
          <Plus className="mr-2 h-4 w-4" /> New Exam
        </Button>
      </PageHeader>

      {/* Search bar */}
      {!isEmpty && (
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search exams..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9 cursor-text"
          />
        </div>
      )}

      {/* Empty state */}
      {isEmpty ? (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
            <div className="rounded-2xl bg-primary/10 p-5">
              <FileText className="h-10 w-10 text-primary" />
            </div>
            <div>
              <h3 className="font-heading font-semibold text-lg">No exams yet</h3>
              <p className="text-muted-foreground text-sm mt-1 max-w-xs">
                Create your first exam to get started. You can add questions, generate answer
                sheets, and scan student responses.
              </p>
            </div>
            <Button
              onClick={() => setFormOpen(true)}
              className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
            >
              <Plus className="mr-2 h-4 w-4" /> Create your first exam
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
                <ExamList exams={paginated} />
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

      <ExamForm open={formOpen} onOpenChange={setFormOpen} />
    </div>
  );
}
