import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export default function TeacherManagement() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  const { data: teachers = [], isLoading } = useQuery({
    queryKey: ["admin", "teachers"],
    queryFn: () => fetchAPI("/admin/teachers"),
  });

  const createMutation = useMutation({
    mutationFn: (data) =>
      fetchAPI("/admin/teachers", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "teachers"] });
      setForm({ name: "", email: "", password: "" });
      setShowForm(false);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id) => fetchAPI(`/admin/teachers/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "teachers"] }),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate(form);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Teacher Management</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          {showForm ? "Cancel" : "Add Teacher"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="rounded-lg border border-border p-4 space-y-3">
          <input
            type="text"
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
          />
          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            required
            minLength={8}
          />
          {createMutation.isError && (
            <p className="text-sm text-destructive">{createMutation.error.message}</p>
          )}
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {createMutation.isPending ? "Creating..." : "Create Teacher"}
          </button>
        </form>
      )}

      {isLoading ? (
        <p className="text-muted-foreground">Loading teachers...</p>
      ) : (
        <div className="space-y-2">
          {teachers.map((teacher) => (
            <div
              key={teacher.id}
              className="flex items-center justify-between rounded-lg border border-border p-4"
            >
              <div>
                <div className="font-medium">{teacher.name}</div>
                <div className="text-sm text-muted-foreground">{teacher.email}</div>
                <div className="flex gap-2 mt-1">
                  {teacher.is_admin && (
                    <span className="text-xs rounded bg-primary/10 text-primary px-2 py-0.5">Admin</span>
                  )}
                  {!teacher.is_active && (
                    <span className="text-xs rounded bg-destructive/10 text-destructive px-2 py-0.5">Disabled</span>
                  )}
                </div>
              </div>
              {teacher.is_active && !teacher.is_admin && (
                <button
                  onClick={() => deactivateMutation.mutate(teacher.id)}
                  className="text-sm text-destructive hover:underline"
                >
                  Deactivate
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
