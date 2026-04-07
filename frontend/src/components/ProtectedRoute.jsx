import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";

export default function ProtectedRoute({ role, requireAdmin }) {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user.role !== role) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive text-lg">403 — Access Denied</div>
      </div>
    );
  }

  if (requireAdmin && !user.is_admin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-destructive text-lg">403 — Admin Access Required</div>
      </div>
    );
  }

  return <Outlet />;
}
