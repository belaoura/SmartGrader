import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ClipboardList,
  ScanLine,
  GraduationCap,
  BarChart3,
  BookOpen,
  FileImage,
  Code2,
  Archive,
  Brain,
  Settings,
  HelpCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navGroups = [
  {
    label: "Main",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", to: "/" },
      { icon: ClipboardList,   label: "Exams",     to: "/exams" },
      { icon: ScanLine,        label: "Scanner",   to: "/scanner" },
      { icon: GraduationCap,   label: "Students",  to: "/students" },
      { icon: BarChart3,       label: "Results",   to: "/results" },
    ],
  },
  {
    label: "Documentation",
    items: [
      { icon: BookOpen,   label: "Academic Thesis", to: "/academic-docs" },
      { icon: FileImage,  label: "Sample Data",     to: "/samples" },
      { icon: Code2,      label: "API Reference",   to: "/documentation" },
      { icon: Archive,    label: "Legacy App",      to: "/legacy" },
    ],
  },
  {
    label: "System",
    items: [
      { icon: Brain,      label: "AI Configuration", to: "/ai-config" },
      { icon: Settings,   label: "Settings",          to: "/settings" },
      { icon: HelpCircle, label: "Help & Guide",      to: "/help" },
    ],
  },
];

function NavItem({ icon: Icon, label, to, onClose }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      onClick={onClose}
      className={({ isActive }) =>
        cn(
          "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium cursor-pointer",
          "transition-all duration-200 ease-in-out",
          isActive
            ? [
                "bg-primary/10 text-primary",
                "before:absolute before:left-0 before:top-1/2 before:-translate-y-1/2",
                "before:h-5 before:w-[3px] before:rounded-r before:bg-primary",
              ].join(" ")
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground hover:-translate-y-px"
        )
      }
    >
      <Icon className="h-[18px] w-[18px] shrink-0" />
      <span>{label}</span>
    </NavLink>
  );
}

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed top-16 bottom-0 z-50 flex w-72 flex-col",
          "backdrop-blur-xl border-r border-border bg-sidebar",
          "transition-transform duration-200 ease-in-out",
          "lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-3 px-2">
          {navGroups.map((group, groupIndex) => (
            <div key={group.label}>
              {/* Group separator line (not before first group) */}
              {groupIndex > 0 && (
                <div className="mx-3 my-2 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
              )}

              {/* Group label */}
              <p className="px-3 pt-3 pb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground select-none">
                {group.label}
              </p>

              {/* Group items */}
              <div className="space-y-0.5">
                {group.items.map(({ icon, label, to }) => (
                  <NavItem
                    key={to}
                    icon={icon}
                    label={label}
                    to={to}
                    onClose={onClose}
                  />
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-border px-4 py-3 flex items-center gap-2">
          <span
            className="inline-block h-2 w-2 rounded-full bg-primary shadow-sm"
            style={{ boxShadow: "0 0 6px rgba(99,102,241,0.6)" }}
          />
          <span className="text-xs text-muted-foreground font-medium">
            SmartGrader v0.3.0
          </span>
        </div>
      </aside>
    </>
  );
}
