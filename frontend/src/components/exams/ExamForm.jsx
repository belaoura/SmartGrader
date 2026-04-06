import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateExam } from "@/hooks/use-exams";

export default function ExamForm({ open, onOpenChange }) {
  const [form, setForm] = useState({ title: "", subject: "", date: "", total_marks: "" });
  const createExam = useCreateExam();

  const handleSubmit = (e) => {
    e.preventDefault();
    createExam.mutate(
      {
        title: form.title,
        subject: form.subject || null,
        date: form.date || null,
        total_marks: form.total_marks ? parseFloat(form.total_marks) : null,
      },
      {
        onSuccess: () => {
          setForm({ title: "", subject: "", date: "", total_marks: "" });
          onOpenChange(false);
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="font-heading">New Exam</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              value={form.subject}
              onChange={(e) => setForm({ ...form, subject: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="marks">Total Marks</Label>
              <Input
                id="marks"
                type="number"
                value={form.total_marks}
                onChange={(e) => setForm({ ...form, total_marks: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!form.title || createExam.isPending} className="cursor-pointer">
              {createExam.isPending ? "Creating..." : "Create Exam"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
