import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

export default function OCRResults({ answers, onUpdateAnswer }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-base">Extracted Answers (edit if needed)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {answers.map((a) => (
          <div key={a.question_id} className="space-y-1">
            <Label>Question {a.question_id}</Label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={a.text}
              onChange={(e) => onUpdateAnswer(a.question_id, e.target.value)}
            />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
