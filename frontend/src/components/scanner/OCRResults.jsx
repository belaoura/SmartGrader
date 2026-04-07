import { Label } from "@/components/ui/label";
import { FileText, Pencil } from "lucide-react";

export default function OCRResults({ answers, onUpdateAnswer }) {
  return (
    <div className="glass rounded-xl overflow-hidden">
      <div className="px-5 py-3 border-b border-border flex items-center gap-2">
        <FileText className="h-4 w-4 text-primary" />
        <h3 className="font-heading font-semibold text-sm">Extracted Answers</h3>
        <span className="text-xs text-muted-foreground ml-auto">Edit if the OCR made mistakes</span>
      </div>
      <div className="divide-y divide-border">
        {answers.map((a, idx) => (
          <div key={a.question_id} className="p-4 space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center">
                <span className="text-[10px] font-bold text-primary">{idx + 1}</span>
              </div>
              <Label className="text-xs font-medium">Question {a.question_id}</Label>
              <Pencil className="h-3 w-3 text-muted-foreground ml-auto" />
            </div>
            <textarea
              className="flex min-h-[60px] w-full rounded-lg border border-input bg-background/50 px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
              value={a.text}
              onChange={(e) => onUpdateAnswer(a.question_id, e.target.value)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
