import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateStudent } from "@/hooks/use-students";

export default function StudentForm({ open, onOpenChange }) {
  const [form, setForm] = useState({ name: "", matricule: "", email: "" });
  const createStudent = useCreateStudent();

  const handleSubmit = (e) => {
    e.preventDefault();
    createStudent.mutate(
      { name: form.name, matricule: form.matricule, email: form.email || null },
      {
        onSuccess: () => {
          setForm({ name: "", matricule: "", email: "" });
          onOpenChange(false);
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="font-heading">Add Student</DialogTitle>
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
            <Button type="submit" disabled={!form.name || !form.matricule || createStudent.isPending} className="cursor-pointer">
              {createStudent.isPending ? "Adding..." : "Add Student"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
