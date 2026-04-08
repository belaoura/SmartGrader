import { Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";

export default function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 h-16 border-b border-border bg-background/80 backdrop-blur-sm flex items-center justify-between px-6">
        <span className="font-semibold">SmartGrader</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{user?.name}</span>
          <button onClick={handleLogout} className="rounded-lg p-2 text-muted-foreground hover:bg-accent transition-colors" title="Sign out">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
