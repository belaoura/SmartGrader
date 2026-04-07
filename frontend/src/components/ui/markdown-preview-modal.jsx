import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { X, Printer } from "lucide-react";
import { Button } from "@/components/ui/button";

function markdownToHtml(md) {
  let html = md
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre class="md-code-block"><code>${code.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>`)
    .replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
    .replace(/^######\s+(.+)$/gm, '<h6 class="md-h6">$1</h6>')
    .replace(/^#####\s+(.+)$/gm, '<h5 class="md-h5">$1</h5>')
    .replace(/^####\s+(.+)$/gm, '<h4 class="md-h4">$1</h4>')
    .replace(/^###\s+(.+)$/gm, '<h3 class="md-h3">$1</h3>')
    .replace(/^##\s+(.+)$/gm, '<h2 class="md-h2">$1</h2>')
    .replace(/^#\s+(.+)$/gm, '<h1 class="md-h1">$1</h1>')
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^>\s+(.+)$/gm, '<blockquote class="md-blockquote">$1</blockquote>')
    .replace(/^---+$/gm, '<hr class="md-hr" />')
    .replace(/^[-*]\s+(.+)$/gm, '<li class="md-li">$1</li>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="md-link" target="_blank">$1</a>')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<span class="md-img-placeholder">[$1]</span>')
    .replace(/^(?!<[a-z]|$)(.+)$/gm, '<p class="md-p">$1</p>');
  html = html.replace(/((?:<li class="md-li">.*<\/li>\s*)+)/g, '<ul class="md-ul">$1</ul>');
  return html;
}

const MD_STYLES = `
  .md-h1 { font-size: 1.75rem; font-weight: 700; margin: 1.5rem 0 0.75rem; font-family: var(--font-heading); }
  .md-h2 { font-size: 1.5rem; font-weight: 600; margin: 1.25rem 0 0.5rem; font-family: var(--font-heading); border-bottom: 1px solid var(--color-border); padding-bottom: 0.25rem; }
  .md-h3 { font-size: 1.25rem; font-weight: 600; margin: 1rem 0 0.5rem; font-family: var(--font-heading); }
  .md-h4 { font-size: 1.1rem; font-weight: 600; margin: 0.75rem 0 0.5rem; }
  .md-h5, .md-h6 { font-size: 1rem; font-weight: 600; margin: 0.5rem 0; }
  .md-p { margin: 0.5rem 0; line-height: 1.7; }
  .md-blockquote { border-left: 3px solid var(--color-primary); padding: 0.5rem 1rem; margin: 0.75rem 0; color: var(--color-muted-foreground); background: var(--color-muted); border-radius: 0.25rem; }
  .md-code-block { background: var(--color-muted); padding: 1rem; border-radius: 0.5rem; overflow-x: auto; font-size: 0.85rem; margin: 0.75rem 0; }
  .md-inline-code { background: var(--color-muted); padding: 0.15rem 0.4rem; border-radius: 0.25rem; font-size: 0.9em; }
  .md-ul { padding-left: 1.5rem; margin: 0.5rem 0; }
  .md-li { margin: 0.25rem 0; list-style-type: disc; }
  .md-link { color: var(--color-primary); text-decoration: underline; }
  .md-hr { border: none; border-top: 1px solid var(--color-border); margin: 1.5rem 0; }
  .md-img-placeholder { display: inline-block; background: var(--color-muted); color: var(--color-muted-foreground); padding: 0.25rem 0.75rem; border-radius: 0.25rem; font-style: italic; font-size: 0.85rem; }
`;

export function MarkdownPreviewModal({ open, onClose, filePath, title }) {
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open || !filePath) return;
    setLoading(true);
    setError(null);
    fetch(`/api/files/${filePath}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.text();
      })
      .then((t) => setContent(t))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [open, filePath]);

  if (!open) return null;

  const html = markdownToHtml(content);

  const handlePrint = () => {
    const win = window.open("", "_blank");
    win.document.write(`<!DOCTYPE html><html><head><title>${title || "Document"}</title>
      <style>
        body { font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.6; max-width: 21cm; margin: 0 auto; padding: 2cm; color: #1a1a1a; }
        h1 { font-size: 22pt; } h2 { font-size: 18pt; } h3 { font-size: 14pt; }
        pre { background: #f5f5f5; padding: 12px; border-radius: 4px; font-size: 10pt; overflow-wrap: break-word; }
        code { font-family: monospace; font-size: 10pt; }
        blockquote { border-left: 3px solid #6366F1; padding-left: 12px; color: #555; }
        table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ddd; padding: 6px 10px; }
        @page { size: A4; margin: 2cm; }
      </style></head><body>${html}</body></html>`);
    win.document.close();
    win.onload = () => win.print();
  };

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative z-10 w-full max-w-4xl max-h-[85vh] flex flex-col rounded-2xl bg-card border border-border shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="font-heading font-semibold text-lg text-foreground">{title || filePath}</h3>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handlePrint} className="cursor-pointer">
              <Printer className="h-4 w-4 mr-1.5" /> Print
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose} className="cursor-pointer">
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-6">
          <style>{MD_STYLES}</style>
          {loading && <p className="text-muted-foreground">Loading...</p>}
          {error && <p className="text-destructive">Error: {error}</p>}
          {content && <div dangerouslySetInnerHTML={{ __html: html }} />}
        </div>
      </div>
    </div>,
    document.body
  );
}
