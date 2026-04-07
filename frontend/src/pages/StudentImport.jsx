import { useState, useRef } from "react";
import { uploadFile } from "@/lib/api";

export default function StudentImport() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file || !file.name.endsWith(".csv")) {
      setError("Please select a CSV file");
      return;
    }
    setError("");
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.trim().split("\n");
      const headers = lines[0].split(",").map((h) => h.trim());
      const rows = lines.slice(1, 6).map((line) =>
        line.split(",").map((cell) => cell.trim())
      );
      setPreview({ headers, rows, total: lines.length - 1 });
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files[0];
    if (!file) return;

    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const data = await uploadFile("/admin/students/import", formData);
      setResult(data);
      setPreview(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Import Students (CSV)</h1>

      <div className="rounded-lg border border-dashed border-border p-8 text-center">
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          onChange={(e) => handleFile(e.target.files[0])}
          className="hidden"
          id="csv-upload"
        />
        <label htmlFor="csv-upload" className="cursor-pointer">
          <div className="text-muted-foreground">
            <p className="text-lg font-medium">Click to select CSV file</p>
            <p className="text-sm mt-1">Expected columns: name, matricule, email</p>
          </div>
        </label>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {preview && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Preview ({preview.total} rows total, showing first 5):
          </p>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-muted">
                  {preview.headers.map((h, i) => (
                    <th key={i} className="px-4 py-2 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i} className="border-t border-border">
                    {row.map((cell, j) => (
                      <td key={j} className="px-4 py-2">{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={handleUpload}
            disabled={loading}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Importing..." : `Import ${preview.total} students`}
          </button>
        </div>
      )}

      {result && (
        <div className="rounded-lg border border-border p-4 space-y-2">
          <h3 className="font-medium">Import Complete</h3>
          <div className="text-sm space-y-1">
            <p className="text-green-500">Created: {result.created}</p>
            <p className="text-yellow-500">Skipped (duplicates): {result.skipped}</p>
            {result.errors.length > 0 && (
              <div>
                <p className="text-destructive">Errors: {result.errors.length}</p>
                <ul className="list-disc list-inside text-destructive mt-1">
                  {result.errors.map((err, i) => (
                    <li key={i}>Row {err.row}: {err.message}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
