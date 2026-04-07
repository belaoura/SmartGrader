import { HelpCircle } from "lucide-react";

/**
 * HelpTooltip – a small question-mark icon that shows `text` on hover.
 *
 * Props:
 *   text (string) – the tooltip content
 */
export function HelpTooltip({ text }) {
  return (
    <span className="relative group inline-flex items-center">
      <HelpCircle
        className="h-4 w-4 cursor-help shrink-0 text-muted-foreground"
        aria-label={text}
      />

      {/* Tooltip bubble */}
      <span
        role="tooltip"
        className={[
          "pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50",
          "w-56 rounded-lg px-3 py-2 text-xs leading-relaxed",
          "opacity-0 scale-95 transition-all duration-150 ease-out",
          "group-hover:opacity-100 group-hover:scale-100",
          "glass shadow-lg text-foreground",
        ].join(" ")}
        style={{
          transformOrigin: "bottom center",
        }}
      >
        {text}
        {/* Arrow */}
        <span
          className="absolute top-full left-1/2 -translate-x-1/2 -mt-px"
          style={{
            width: 0,
            height: 0,
            borderLeft: "5px solid transparent",
            borderRight: "5px solid transparent",
            borderTop: "5px solid var(--color-border)",
          }}
        />
      </span>
    </span>
  );
}
