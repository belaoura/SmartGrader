import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateStudent, useUpdateStudent } from "@/hooks/use-students";

export default function StudentForm({ open, onOpenChange, student = null }) {
  const [form, setForm] = useState({ name: "", matricule: "", email: "" });
  const createStudent = useCreateStudent();
  const updateStudent = useUpdateStudent();
  const isEdit = !!student;

  useEffect(() => {
    if (student) {
      setForm({ name: student.name || "", matricule: student.matricule || "", email: student.email || "" });
    } else {
      setForm({ name: "", matricule: "", email: "" });
    }
  }, [student, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const mutation = isEdit ? updateStudent : createStudent;
    const payload = isEdit
      ? { id: student.id, name: form.name, matricule: form.matricule, email: form.email || null }
      : { name: form.name, matricule: form.matricule, email: form.email || null };

    mutation.mutate(payload, {
      onSuccess: () => {
        setForm({ name: "", matricule: "", email: "" });
        onOpenChange(false);
      },
    });
  };

  const isPending = createStudent.isPending || updateStudent.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="font-heading">{isEdit ? "Edit Student" : "Add Student"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="matricule">Matricule *</Label>
            <Input id="matricule" value={form.matricule} onChange={(e) => setForm({ ...form, matricule: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!form.name || !form.matricule || isPending} className="cursor-pointer">
              {isPending ? (isEdit ? "Saving..." : "Adding...") : (isEdit ? "Save Changes" : "Add Student")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
