import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import BarcodeScanner from "@/components/BarcodeScanner";
import {
  GraduationCap,
  Mail,
  Lock,
  ScanLine,
  Keyboard,
  ShieldCheck,
  Brain,
  Monitor,
  Eye,
  ChevronRight,
  AlertCircle,
  Loader2,
  BookOpen,
  Users,
  BarChart3,
  Camera,
} from "lucide-react";

function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950" />

      {/* Animated gradient orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-600/20 blur-[120px] animate-[float_8s_ease-in-out_infinite]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/20 blur-[120px] animate-[float_10s_ease-in-out_infinite_reverse]" />
      <div className="absolute top-[40%] left-[50%] w-[400px] h-[400px] rounded-full bg-blue-600/10 blur-[100px] animate-[float_12s_ease-in-out_infinite_2s]" />

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Floating particles */}
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-white/20"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animation: `float ${6 + Math.random() * 8}s ease-in-out infinite ${Math.random() * 5}s`,
          }}
        />
      ))}
    </div>
  );
}

function FeatureCard({ icon: Icon, title, desc }) {
  return (
    <div className="flex items-start gap-3 rounded-xl bg-white/5 border border-white/10 p-3 backdrop-blur-sm transition-all duration-300 hover:bg-white/10 hover:border-white/20 hover:translate-y-[-2px]">
      <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-indigo-500/20 flex items-center justify-center">
        <Icon className="w-4 h-4 text-indigo-300" />
      </div>
      <div>
        <div className="text-sm font-medium text-white/90">{title}</div>
        <div className="text-xs text-white/50 mt-0.5 leading-relaxed">{desc}</div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  const [tab, setTab] = useState("teacher");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [matricule, setMatricule] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);

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
    <div className="relative flex min-h-screen text-white">
      <AnimatedBackground />

      {/* Left panel — branding & features */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 xl:p-16">
        {/* Logo + tagline */}
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <GraduationCap className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">SmartGrader</h1>
              <p className="text-xs text-white/50 font-medium tracking-wide uppercase">AI-Powered Exam Platform</p>
            </div>
          </div>
          <p className="mt-6 text-lg text-white/70 leading-relaxed max-w-md">
            The complete exam management system — from creating questions to AI-powered grading,
            online proctored exams, and instant analytics.
          </p>
        </div>

        {/* Feature cards */}
        <div className="space-y-3 max-w-md">
          <p className="text-xs font-semibold uppercase tracking-wider text-white/40 mb-4">Platform Features</p>
          <FeatureCard icon={BookOpen} title="Exam Management" desc="Create, organize, and manage MCQ exams with printable answer sheets" />
          <FeatureCard icon={Brain} title="AI-Powered Grading" desc="Automatic MCQ scanning with OpenCV + AI short-answer evaluation" />
          <FeatureCard icon={Monitor} title="Online Exams" desc="Students take exams in-browser with timer, auto-save, and live monitoring" />
          <FeatureCard icon={Eye} title="Anti-Cheat Proctoring" desc="Webcam face detection, tab tracking, and configurable cheat response" />
          <FeatureCard icon={BarChart3} title="Analytics & Results" desc="Instant grading, score breakdown, and exportable result reports" />
          <FeatureCard icon={Users} title="Group Management" desc="Organize students into groups for easy exam assignment" />
        </div>

        {/* Footer */}
        <div className="flex items-center gap-2 text-white/30 text-xs">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Secure JWT Authentication &bull; PFE Academic Project &bull; v1.0.0</span>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 justify-center mb-8">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">SmartGrader</h1>
              <p className="text-[10px] text-white/50 uppercase tracking-wide">AI-Powered Exam Platform</p>
            </div>
          </div>

          {/* Glass card */}
          <div className="rounded-2xl bg-white/[0.07] border border-white/[0.12] backdrop-blur-xl shadow-2xl shadow-black/20 p-8">
            <div className="text-center mb-6">
              <h2 className="text-xl font-semibold">Welcome back</h2>
              <p className="text-sm text-white/50 mt-1">Sign in to access the platform</p>
            </div>

            {/* Tab switcher */}
            <div className="flex rounded-xl bg-white/[0.06] p-1 mb-6">
              <button
                className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-300 ${
                  tab === "teacher"
                    ? "bg-gradient-to-r from-indigo-500 to-indigo-600 text-white shadow-lg shadow-indigo-500/25"
                    : "text-white/50 hover:text-white/80"
                }`}
                onClick={() => { setTab("teacher"); setError(""); }}
              >
                <Mail className="w-4 h-4" />
                Teacher
              </button>
              <button
                className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-300 ${
                  tab === "student"
                    ? "bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg shadow-purple-500/25"
                    : "text-white/50 hover:text-white/80"
                }`}
                onClick={() => { setTab("student"); setError(""); }}
              >
                <ScanLine className="w-4 h-4" />
                Student
              </button>
            </div>

            {/* Error message */}
            {error && (
              <div className="flex items-center gap-2 rounded-xl bg-red-500/10 border border-red-500/20 p-3 mb-5 animate-[shake_0.3s_ease-in-out]">
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                <span className="text-sm text-red-300">{error}</span>
              </div>
            )}

            {/* Teacher form */}
            {tab === "teacher" && (
              <form onSubmit={handleTeacherLogin} className="space-y-4">
                <div>
                  <label className="flex items-center gap-1.5 text-sm font-medium text-white/70 mb-2">
                    <Mail className="w-3.5 h-3.5" />
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all duration-200 focus:border-indigo-500/50 focus:bg-white/[0.08] focus:ring-2 focus:ring-indigo-500/20"
                    placeholder="teacher@university.dz"
                    required
                    autoComplete="email"
                  />
                </div>
                <div>
                  <label className="flex items-center gap-1.5 text-sm font-medium text-white/70 mb-2">
                    <Lock className="w-3.5 h-3.5" />
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all duration-200 focus:border-indigo-500/50 focus:bg-white/[0.08] focus:ring-2 focus:ring-indigo-500/20"
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !email || !password}
                  className="group w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all duration-300 hover:shadow-indigo-500/40 hover:translate-y-[-1px] disabled:opacity-50 disabled:hover:translate-y-0"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      Sign In
                      <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                    </>
                  )}
                </button>

                <div className="pt-2 text-center">
                  <p className="text-xs text-white/30">
                    Contact your administrator if you don't have an account
                  </p>
                </div>
              </form>
            )}

            {/* Student form */}
            {tab === "student" && (
              <div className="space-y-4">
                {/* Instructions */}
                <div className="rounded-xl bg-purple-500/10 border border-purple-500/20 p-4">
                  <p className="text-sm font-medium text-purple-300 mb-2">How to sign in:</p>
                  <ul className="space-y-1.5 text-xs text-white/50">
                    <li className="flex items-center gap-2">
                      <Camera className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                      Scan your student card barcode using webcam
                    </li>
                    <li className="flex items-center gap-2">
                      <ScanLine className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                      Or use a USB barcode scanner (auto-detects)
                    </li>
                    <li className="flex items-center gap-2">
                      <Keyboard className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                      Or type your matricule number manually
                    </li>
                  </ul>
                </div>

                {/* Camera scanner toggle */}
                {!showScanner ? (
                  <button
                    type="button"
                    onClick={() => setShowScanner(true)}
                    className="w-full flex items-center justify-center gap-2 rounded-xl border-2 border-dashed border-white/15 bg-white/[0.03] px-4 py-6 text-sm text-white/50 transition-all hover:border-purple-500/30 hover:bg-purple-500/5 hover:text-white/70"
                  >
                    <Camera className="w-5 h-5" />
                    Open Camera Scanner
                  </button>
                ) : (
                  <div className="rounded-xl overflow-hidden border border-white/10">
                    <BarcodeScanner
                      onScan={(code) => { setShowScanner(false); handleStudentLogin(code); }}
                      onError={(msg) => setError(msg)}
                    />
                  </div>
                )}

                {/* Divider */}
                <div className="flex items-center gap-3">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/15 to-transparent" />
                  <span className="text-xs text-white/30 font-medium">or enter manually</span>
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/15 to-transparent" />
                </div>

                {/* Manual matricule input */}
                <form onSubmit={(e) => { e.preventDefault(); handleStudentLogin(); }} className="space-y-4">
                  <div>
                    <label className="flex items-center gap-1.5 text-sm font-medium text-white/70 mb-2">
                      <Keyboard className="w-3.5 h-3.5" />
                      Matricule Number
                    </label>
                    <input
                      ref={matriculeRef}
                      type="text"
                      value={matricule}
                      onChange={(e) => setMatricule(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm text-white placeholder-white/30 outline-none transition-all duration-200 focus:border-purple-500/50 focus:bg-white/[0.08] focus:ring-2 focus:ring-purple-500/20"
                      placeholder="e.g., 2026001"
                      autoFocus
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading || !matricule.trim()}
                    className="group w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-purple-500/25 transition-all duration-300 hover:shadow-purple-500/40 hover:translate-y-[-1px] disabled:opacity-50 disabled:hover:translate-y-0"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        Sign In with Matricule
                        <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                      </>
                    )}
                  </button>
                </form>
              </div>
            )}
          </div>

          {/* Bottom info */}
          <div className="mt-6 text-center space-y-2">
            <div className="flex items-center justify-center gap-4 text-xs text-white/25">
              <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3" /> Encrypted</span>
              <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> Proctored</span>
              <span className="flex items-center gap-1"><Brain className="w-3 h-3" /> AI-Powered</span>
            </div>
          </div>
        </div>
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
      `}</style>
    </div>
  );
}
