import { HelpTooltip } from "@/components/ui/help-tooltip";

/**
 * PageHeader – reusable page-level heading.
 *
 * Props:
 *   title       (string)  – required, rendered as h2
 *   description (string)  – optional subtitle below the title
 *   helpText    (string)  – optional text shown in a HelpTooltip next to the title
 *   children    (node)    – optional action buttons rendered on the right
 */
export function PageHeader({ title, description, helpText, children }) {
  return (
    <div className="flex flex-col gap-1 mb-6 sm:flex-row sm:items-start sm:justify-between">
      {/* Left: title + description */}
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <h2
            className="text-2xl font-bold leading-tight font-heading text-foreground"
          >
            {title}
          </h2>
          {helpText && <HelpTooltip text={helpText} />}
        </div>
        {description && (
          <p
            className="text-sm text-muted-foreground"
          >
            {description}
          </p>
        )}
      </div>

      {/* Right: action slot */}
      {children && (
        <div className="flex items-center gap-2 shrink-0 mt-2 sm:mt-0">
          {children}
        </div>
      )}
    </div>
  );
}
