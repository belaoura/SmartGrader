import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { X, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

function highlightJSON(json) {
  return json
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"([^"]+)"(\s*:)/g, '<span class="text-primary font-semibold">"$1"</span>$2')
    .replace(/:\s*"([^"]*)"/g, ': <span class="text-emerald-600 dark:text-emerald-400">"$1"</span>')
    .replace(/:\s*(\d+\.?\d*)/g, ': <span class="text-blue-600 dark:text-blue-400">$1</span>')
    .replace(/:\s*(true|false)/g, ': <span class="text-amber-600 dark:text-amber-400">$1</span>')
    .replace(/:\s*(null)/g, ': <span class="text-rose-500">$1</span>');
}

export function JsonPreviewModal({ open, onClose, filename, title }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open || !filename) return;
    setLoading(true);
    setError(null);
    fetch(`/api/files/old files/${filename}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => setData(d))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [open, filename]);

  if (!open) return null;

  const prettyJson = data ? JSON.stringify(data, null, 2) : "";

  const handleCopy = () => {
    navigator.clipboard.writeText(prettyJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative z-10 w-full max-w-3xl max-h-[85vh] flex flex-col rounded-2xl bg-card border border-border shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="font-heading font-semibold text-lg text-foreground">{title || filename}</h3>
          <div className="flex items-center gap-2">
            {data && (
              <Button variant="outline" size="sm" onClick={handleCopy} className="cursor-pointer">
                {copied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                <span className="ml-1.5">{copied ? "Copied" : "Copy"}</span>
              </Button>
            )}
            <Button variant="ghost" size="icon" onClick={onClose} className="cursor-pointer">
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-6">
          {loading && <p className="text-muted-foreground">Loading...</p>}
          {error && <p className="text-destructive">Error: {error}</p>}
          {data && (
            <pre
              className="text-sm font-mono leading-relaxed whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: highlightJSON(prettyJson) }}
            />
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}
