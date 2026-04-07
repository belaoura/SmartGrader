import { Mail, Hash } from "lucide-react";

export default function StudentList({ students }) {
  if (students.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-12 px-6">
        No students match your search.
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {students.map((s, idx) => (
        <div
          key={s.id}
          className="group flex items-center gap-4 px-5 py-4 hover:bg-accent/40 transition-all duration-200"
        >
          {/* Avatar */}
          <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
            <span className="text-xs font-bold text-primary">
              {s.name?.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase()}
            </span>
          </div>

          {/* Main info */}
          <div className="flex-1 min-w-0">
            <h4 className="font-heading font-semibold text-sm truncate">{s.name}</h4>
            <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
              <span className="flex items-center gap-1">
                <Hash className="h-3 w-3" />
                {s.matricule}
              </span>
              {s.email && (
                <span className="flex items-center gap-1 truncate">
                  <Mail className="h-3 w-3 shrink-0" />
                  {s.email}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
