import { useState, useEffect } from "react";
import { X, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

function textToHex(text) {
  return Array.from(new TextEncoder().encode(text))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function PumlPreviewModal({ open, onClose, filename, title }) {
  const [source, setSource] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [imgError, setImgError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open || !filename) return;
    setLoading(true);
    setError(null);
    setImgError(false);
    fetch(`/api/files/docs/figures/uml/${filename}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.text();
      })
      .then((text) => {
        setSource(text);
        const hex = textToHex(text);
        setImgUrl(`https://www.plantuml.com/plantuml/svg/~h${hex}`);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [open, filename]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative z-10 w-full max-w-5xl max-h-[90vh] flex flex-col rounded-2xl bg-card border border-border shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="font-heading font-semibold text-lg text-foreground">{title || filename}</h3>
          <Button variant="ghost" size="icon" onClick={onClose} className="cursor-pointer">
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 overflow-auto p-6 flex items-start justify-center">
          {loading && <p className="text-muted-foreground">Loading diagram source...</p>}
          {error && <p className="text-destructive">Error: {error}</p>}
          {imgUrl && !imgError && (
            <img
              src={imgUrl}
              alt={title || filename}
              className="max-w-full h-auto"
              onError={() => setImgError(true)}
            />
          )}
          {imgError && source && (
            <div className="w-full space-y-3">
              <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                <AlertCircle className="h-5 w-5" />
                <span className="text-sm font-medium">Could not render diagram. Showing source:</span>
              </div>
              <pre className="text-sm font-mono bg-muted p-4 rounded-xl overflow-auto max-h-[60vh] whitespace-pre-wrap">
                {source}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
