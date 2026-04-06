import { NavLink } from "react-router-dom";
import { LayoutDashboard, FileText, ScanLine, Users, BarChart3, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", to: "/" },
  { icon: FileText, label: "Exams", to: "/exams" },
  { icon: ScanLine, label: "Scanner", to: "/scanner" },
  { icon: Users, label: "Students", to: "/students" },
  { icon: BarChart3, label: "Results", to: "/results" },
  { icon: Settings, label: "Settings", to: "/settings" },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={cn(
          "fixed top-16 bottom-0 z-50 flex w-64 flex-col border-r border-border bg-sidebar",
          "transition-transform duration-200 ease-in-out",
          "lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <nav className="flex-1 space-y-1 p-3">
          {navItems.map(({ icon: Icon, label, to }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors cursor-pointer",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )
              }
            >
              <Icon className="h-5 w-5 shrink-0" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-border p-3 text-xs text-muted-foreground">
          SmartGrader v0.2.0
        </div>
      </aside>
    </>
  );
}
