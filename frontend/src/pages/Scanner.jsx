import { useState } from "react";
import { ScanLine, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { useExams } from "@/hooks/use-exams";
import { uploadFile } from "@/lib/api";
import UploadZone from "@/components/scanner/UploadZone";
import ScanResults from "@/components/scanner/ScanResults";

export default function Scanner() {
  const [examId, setExamId] = useState("");
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const { data: exams } = useExams();

  const handleScan = async () => {
    if (!file || !examId) return;
    setScanning(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("exam_id", examId);

    try {
      const data = await uploadFile("/scan/upload", formData);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold font-heading">Scanner</h2>

      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-base">Scan Answer Sheet</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Select Exam *</Label>
            <Select value={examId} onValueChange={setExamId}>
              <SelectTrigger className="cursor-pointer">
                <SelectValue placeholder="Choose an exam..." />
              </SelectTrigger>
              <SelectContent>
                {(exams || []).map((e) => (
                  <SelectItem key={e.id} value={String(e.id)} className="cursor-pointer">
                    {e.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <UploadZone file={file} onFileChange={setFile} />

          <Button
            onClick={handleScan}
            disabled={!file || !examId || scanning}
            className="w-full cursor-pointer"
          >
            {scanning ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Scanning...</>
            ) : (
              <><ScanLine className="mr-2 h-4 w-4" /> Scan & Grade</>
            )}
          </Button>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </CardContent>
      </Card>

      {result && <ScanResults result={result} />}
    </div>
  );
}
