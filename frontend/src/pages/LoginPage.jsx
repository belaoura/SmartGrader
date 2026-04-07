import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import BarcodeScanner from "@/components/BarcodeScanner";

export default function LoginPage() {
  const [tab, setTab] = useState("teacher");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [matricule, setMatricule] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { loginTeacher, loginStudent, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const matriculeRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(user?.role === "teacher" ? "/" : "/exam", { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleTeacherLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await loginTeacher(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentLogin = async (mat) => {
    const value = mat || matricule;
    if (!value.trim()) return;
    setError("");
    setLoading(true);
    try {
      await loginStudent(value.trim());
      navigate("/exam", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">SmartGrader</h1>
          <p className="text-muted-foreground mt-1">Sign in to continue</p>
        </div>

        <div className="flex rounded-lg bg-muted p-1">
          <button
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === "teacher"
                ? "bg-background shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => { setTab("teacher"); setError(""); }}
          >
            Teacher
          </button>
          <button
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === "student"
                ? "bg-background shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => { setTab("student"); setError(""); }}
          >
            Student
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {tab === "teacher" && (
          <form onSubmit={handleTeacherLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="teacher@university.dz"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="Enter your password"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full rounded-lg bg-primary px-4 py-2 text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>
        )}

        {tab === "student" && (
          <div className="space-y-4">
            <BarcodeScanner
              onScan={(code) => handleStudentLogin(code)}
              onError={(msg) => setError(msg)}
            />

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs text-muted-foreground">or enter manually</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleStudentLogin(); }} className="space-y-4">
              <input
                ref={matriculeRef}
                type="text"
                value={matricule}
                onChange={(e) => setMatricule(e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
                placeholder="Matricule number"
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !matricule.trim()}
                className="w-full rounded-lg bg-primary px-4 py-2 text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {loading ? "Signing in..." : "Login"}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
