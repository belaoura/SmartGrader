import { CheckCircle2, XCircle, MinusCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function ScanResults({ result }) {
  return (
    <div className="space-y-4">
      <Card className="border-primary/20">
        <CardContent className="flex items-center justify-center gap-6 p-8">
          <div className="text-center">
            <p className="text-4xl font-bold font-heading text-primary">
              {result.obtained_marks}/{result.total_marks}
            </p>
            <p className="text-lg text-muted-foreground">
              {result.percentage}%
            </p>
          </div>
          <div className="text-sm text-muted-foreground">
            <p>{result.answered}/{result.total_questions} answered</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-base">Question Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Question</TableHead>
                <TableHead>Detected</TableHead>
                <TableHead>Correct</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {result.details?.map((d) => (
                <TableRow
                  key={d.question_id}
                  className={
                    d.is_correct
                      ? "bg-green-500/5"
                      : d.detected
                      ? "bg-red-500/5"
                      : "bg-amber-500/5"
                  }
                >
                  <TableCell>Q{d.question_id}</TableCell>
                  <TableCell>{d.detected || "-"}</TableCell>
                  <TableCell>{d.correct || "-"}</TableCell>
                  <TableCell>
                    {d.is_correct ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : d.detected ? (
                      <XCircle className="h-5 w-5 text-red-500" />
                    ) : (
                      <MinusCircle className="h-5 w-5 text-amber-500" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
