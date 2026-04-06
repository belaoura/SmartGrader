import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Minus } from "lucide-react";
import { useCreateQuestion } from "@/hooks/use-exams";

const LABELS = ["A", "B", "C", "D", "E", "F"];

export default function QuestionBuilder({ examId, open, onOpenChange }) {
  const [text, setText] = useState("");
  const [marks, setMarks] = useState("1");
  const [choices, setChoices] = useState([
    { label: "A", text: "", is_correct: true },
    { label: "B", text: "", is_correct: false },
    { label: "C", text: "", is_correct: false },
    { label: "D", text: "", is_correct: false },
  ]);

  const createQuestion = useCreateQuestion(examId);

  const addChoice = () => {
    if (choices.length < 6) {
      setChoices([...choices, { label: LABELS[choices.length], text: "", is_correct: false }]);
    }
  };

  const removeChoice = () => {
    if (choices.length > 2) {
      const removed = choices[choices.length - 1];
      const newChoices = choices.slice(0, -1);
      if (removed.is_correct && newChoices.length > 0) {
        newChoices[0].is_correct = true;
      }
      setChoices(newChoices);
    }
  };

  const updateChoiceText = (index, value) => {
    const updated = [...choices];
    updated[index] = { ...updated[index], text: value };
    setChoices(updated);
  };

  const setCorrect = (index) => {
    setChoices(choices.map((c, i) => ({ ...c, is_correct: i === index })));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    createQuestion.mutate(
      { question_text: text, marks: parseFloat(marks), choices },
      {
        onSuccess: () => {
          setText("");
          setMarks("1");
          setChoices([
            { label: "A", text: "", is_correct: true },
            { label: "B", text: "", is_correct: false },
            { label: "C", text: "", is_correct: false },
            { label: "D", text: "", is_correct: false },
          ]);
          onOpenChange(false);
        },
      }
    );
  };

  const isValid = text.trim() && choices.every((c) => c.text.trim()) && choices.some((c) => c.is_correct);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="font-heading">Add Question</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="q-text">Question Text *</Label>
            <textarea
              id="q-text"
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="q-marks">Marks *</Label>
            <Input
              id="q-marks"
              type="number"
              min="0.5"
              step="0.5"
              value={marks}
              onChange={(e) => setMarks(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Choices (select correct answer)</Label>
              <div className="flex gap-1">
                <Button type="button" variant="outline" size="icon" onClick={removeChoice} disabled={choices.length <= 2} className="h-7 w-7 cursor-pointer">
                  <Minus className="h-3 w-3" />
                </Button>
                <Button type="button" variant="outline" size="icon" onClick={addChoice} disabled={choices.length >= 6} className="h-7 w-7 cursor-pointer">
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
            </div>
            {choices.map((choice, i) => (
              <div key={choice.label} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="correct"
                  checked={choice.is_correct}
                  onChange={() => setCorrect(i)}
                  className="h-4 w-4 accent-[var(--color-primary)] cursor-pointer"
                />
                <span className="w-6 text-sm font-medium">{choice.label}.</span>
                <Input
                  placeholder={`Choice ${choice.label}`}
                  value={choice.text}
                  onChange={(e) => updateChoiceText(i, e.target.value)}
                  required
                />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!isValid || createQuestion.isPending} className="cursor-pointer">
              {createQuestion.isPending ? "Saving..." : "Save Question"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
