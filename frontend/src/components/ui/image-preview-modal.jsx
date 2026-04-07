import { createPortal } from "react-dom";
import { X, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ImagePreviewModal({ open, onClose, src, title }) {
  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm" />
      <div
        className="relative z-10 w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl bg-card border border-border shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="font-heading font-semibold text-lg text-foreground truncate">{title}</h3>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="cursor-pointer"
              onClick={() => window.open(src, "_blank")}
            >
              <Download className="h-4 w-4 mr-1.5" /> Open
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose} className="cursor-pointer">
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-4 flex items-center justify-center bg-muted/30">
          <img
            src={src}
            alt={title}
            className="max-w-full max-h-[70vh] object-contain rounded-lg"
            onError={(e) => {
              e.target.style.display = "none";
              e.target.parentNode.innerHTML =
                '<p class="text-muted-foreground text-center p-8">Image could not be loaded. The file may not be served yet.</p>';
            }}
          />
        </div>
      </div>
    </div>,
    document.body
  );
}
