import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/ui/page-header";
import { useExams } from "@/hooks/use-exams";
import { useStudents } from "@/hooks/use-students";
import { useGroups } from "@/hooks/use-groups";
import { useCreateSession, useAssignStudents } from "@/hooks/use-sessions";

function RadioGroup({ label, name, value, onChange, options }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-3">
        {options.map((opt) => (
          <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={name}
              value={opt.value}
              checked={value === opt.value}
              onChange={() => onChange(opt.value)}
              className="accent-primary"
            />
            <span className="text-sm">{opt.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export default function CreateSession() {
  const navigate = useNavigate();
  const { data: exams } = useExams();
  const { data: students } = useStudents();
  const { data: groups } = useGroups();
  const createSession = useCreateSession();
  const assignStudents = useAssignStudents();

  const [form, setForm] = useState({
    exam_id: "",
    start_time: "",
    end_time: "",
    display_mode: "all_at_once",
    save_mode: "auto_each",
    randomize: false,
    show_result: "none",
  });
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [error, setError] = useState("");

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  const toggleItem = (list, setList, id) => {
    setList((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.exam_id) return setError("Please select an exam.");
    if (!form.start_time) return setError("Please set a start time.");
    if (!form.end_time) return setError("Please set an end time.");

    try {
      const session = await createSession.mutateAsync({
        exam_id: Number(form.exam_id),
        start_time: form.start_time,
        end_time: form.end_time,
        display_mode: form.display_mode,
        save_mode: form.save_mode,
        randomize: form.randomize,
        show_result: form.show_result,
      });

      if (selectedStudents.length > 0 || selectedGroups.length > 0) {
        await assignStudents.mutateAsync({
          sessionId: session.id,
          studentIds: selectedStudents,
          groupIds: selectedGroups,
        });
      }

      navigate(`/sessions/${session.id}`);
    } catch (err) {
      setError(err.message || "Failed to create session.");
    }
  };

  const isPending = createSession.isPending || assignStudents.isPending;

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="New Exam Session" description="Configure an online exam session for your students" />

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-lg bg-destructive/10 border border-destructive/30 px-4 py-2 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Exam & Times */}
        <Card className="glass">
          <CardHeader><CardTitle className="text-base">Basic Settings</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="exam_id">Exam</Label>
              <select
                id="exam_id"
                value={form.exam_id}
                onChange={(e) => set("exam_id", e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="">-- Select exam --</option>
                {(exams || []).map((ex) => (
                  <option key={ex.id} value={ex.id}>{ex.title}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_time">Start Time</Label>
                <Input
                  id="start_time"
                  type="datetime-local"
                  value={form.start_time}
                  onChange={(e) => set("start_time", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_time">End Time</Label>
                <Input
                  id="end_time"
                  type="datetime-local"
                  value={form.end_time}
                  onChange={(e) => set("end_time", e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Behaviour */}
        <Card className="glass">
          <CardHeader><CardTitle className="text-base">Exam Behaviour</CardTitle></CardHeader>
          <CardContent className="space-y-5">
            <RadioGroup
              label="Display Mode"
              name="display_mode"
              value={form.display_mode}
              onChange={(v) => set("display_mode", v)}
              options={[
                { value: "all_at_once", label: "All questions at once" },
                { value: "one_by_one", label: "One question at a time" },
              ]}
            />

            <RadioGroup
              label="Save Mode"
              name="save_mode"
              value={form.save_mode}
              onChange={(v) => set("save_mode", v)}
              options={[
                { value: "auto_each", label: "Auto-save each answer" },
                { value: "auto_periodic", label: "Auto-save every 30s" },
                { value: "manual", label: "Manual save" },
              ]}
            />

            <RadioGroup
              label="Show Result"
              name="show_result"
              value={form.show_result}
              onChange={(v) => set("show_result", v)}
              options={[
                { value: "none", label: "Don't show" },
                { value: "score_only", label: "Score only" },
                { value: "score_and_answers", label: "Score + answers" },
              ]}
            />

            <div className="flex items-center gap-2">
              <input
                id="randomize"
                type="checkbox"
                checked={form.randomize}
                onChange={(e) => set("randomize", e.target.checked)}
                className="accent-primary h-4 w-4"
              />
              <Label htmlFor="randomize" className="cursor-pointer">Randomize question order</Label>
            </div>
          </CardContent>
        </Card>

        {/* Assign */}
        <Card className="glass">
          <CardHeader><CardTitle className="text-base">Assign Students</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {(groups || []).length > 0 && (
              <div className="space-y-2">
                <Label>Groups</Label>
                <div className="max-h-36 overflow-y-auto border border-border rounded-lg p-2 space-y-1">
                  {(groups || []).map((g) => (
                    <label key={g.id} className="flex items-center gap-2 cursor-pointer rounded px-2 py-1 hover:bg-accent/30">
                      <input
                        type="checkbox"
                        checked={selectedGroups.includes(g.id)}
                        onChange={() => toggleItem(selectedGroups, setSelectedGroups, g.id)}
                        className="accent-primary"
                      />
                      <span className="text-sm">{g.name}</span>
                      <span className="text-xs text-muted-foreground">({g.member_count ?? 0} members)</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {(students || []).length > 0 && (
              <div className="space-y-2">
                <Label>Individual Students</Label>
                <div className="max-h-36 overflow-y-auto border border-border rounded-lg p-2 space-y-1">
                  {(students || []).map((s) => (
                    <label key={s.id} className="flex items-center gap-2 cursor-pointer rounded px-2 py-1 hover:bg-accent/30">
                      <input
                        type="checkbox"
                        checked={selectedStudents.includes(s.id)}
                        onChange={() => toggleItem(selectedStudents, setSelectedStudents, s.id)}
                        className="accent-primary"
                      />
                      <span className="text-sm">{s.name}</span>
                      <span className="text-xs text-muted-foreground">{s.student_id}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {(selectedStudents.length > 0 || selectedGroups.length > 0) && (
              <p className="text-xs text-muted-foreground">
                {selectedStudents.length} student(s) + {selectedGroups.length} group(s) selected
              </p>
            )}
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button type="submit" disabled={isPending} className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200">
            {isPending ? "Creating..." : "Create Session"}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate("/sessions")}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
