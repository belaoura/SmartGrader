import { useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { HelpTooltip } from "@/components/ui/help-tooltip";
import { useTheme } from "@/hooks/use-theme";
import {
  Settings2,
  BookOpen,
  ExternalLink,
  Activity,
  Brain,
  FlaskConical,
  MonitorPlay,
  Database,
  Server,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowRight,
  Palette,
} from "lucide-react";

const TECH_STACK = [
  { name: "Python", color: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20" },
  { name: "Flask", color: "bg-gray-500/10 text-gray-600 dark:text-gray-300 border-gray-500/20" },
  { name: "React", color: "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20" },
  { name: "OpenCV", color: "bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20" },
  { name: "Qwen2.5-VL", color: "bg-violet-500/10 text-violet-600 dark:text-violet-400 border-violet-500/20" },
  { name: "SQLite", color: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20" },
  { name: "TailwindCSS", color: "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20" },
];

const PALETTE = [
  { label: "Primary (Indigo)", color: "#6366F1" },
  { label: "Success (Emerald)", color: "#10B981" },
  { label: "Warning (Amber)", color: "#F59E0B" },
  { label: "Danger (Rose)", color: "#F43F5E" },
  { label: "Violet", color: "#8B5CF6" },
];

const QUICK_LINKS = [
  {
    to: "/ai-config",
    icon: Brain,
    title: "AI Configuration",
    desc: "Configure AI model settings and vision thresholds",
    color: "bg-violet-500/10 text-violet-500",
  },
  {
    to: "/samples",
    icon: FlaskConical,
    title: "Sample Data",
    desc: "Browse sample exam sheets and test datasets",
    color: "bg-emerald-500/10 text-emerald-500",
  },
  {
    to: "/legacy",
    icon: MonitorPlay,
    title: "Legacy App",
    desc: "Original PyQt5 desktop application reference",
    color: "bg-amber-500/10 text-amber-500",
  },
  {
    to: "/documentation",
    icon: BookOpen,
    title: "Documentation",
    desc: "Technical documentation and API reference",
    color: "bg-indigo-500/10 text-indigo-500",
  },
];

function ApiHealthButton() {
  const [status, setStatus] = useState(null); // null | "loading" | "ok" | "error"
  const [detail, setDetail] = useState("");

  const check = async () => {
    setStatus("loading");
    try {
      const res = await fetch("http://localhost:5000/api/health");
      if (res.ok) {
        const data = await res.json();
        setDetail(data.status || "healthy");
        setStatus("ok");
      } else {
        setDetail(`HTTP ${res.status}`);
        setStatus("error");
      }
    } catch (err) {
      setDetail("Cannot reach server");
      setStatus("error");
    }
  };

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <Button
        variant="outline"
        size="sm"
        onClick={check}
        disabled={status === "loading"}
        className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200"
      >
        {status === "loading" ? (
          <><Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" /> Checking...</>
        ) : (
          <><Activity className="mr-2 h-3.5 w-3.5" /> Check API Health</>
        )}
      </Button>
      {status === "ok" && (
        <span className="flex items-center gap-1.5 text-sm text-emerald-600 dark:text-emerald-400 font-medium">
          <CheckCircle2 className="h-4 w-4" /> {detail}
        </span>
      )}
      {status === "error" && (
        <span className="flex items-center gap-1.5 text-sm text-destructive font-medium">
          <XCircle className="h-4 w-4" /> {detail}
        </span>
      )}
    </div>
  );
}

export default function Settings() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Application preferences and system information"
        helpText="Configure appearance, view project information, and check system status."
      />

      {/* 1. Appearance */}
      <Card className="glass">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-indigo-500/10 p-2">
              <Palette className="h-4 w-4 text-indigo-500" />
            </div>
            <CardTitle className="font-heading text-base">Appearance</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Dark mode toggle */}
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-sm font-medium">Dark Mode</Label>
              <p className="text-sm text-muted-foreground">Toggle between light and dark theme</p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={toggleTheme}
              className="cursor-pointer"
            />
          </div>

          <Separator />

          {/* Color palette preview */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label className="text-sm font-medium">Color Palette</Label>
              <HelpTooltip text="These are the main colors used throughout the application." />
            </div>
            <div className="flex flex-wrap gap-3 mt-2">
              {PALETTE.map((p) => (
                <div key={p.label} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <div
                    className="w-6 h-6 rounded-full border-2 border-white/20 shadow-sm"
                    style={{ backgroundColor: p.color }}
                    title={p.label}
                  />
                  <span>{p.label}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 2. Application Info */}
      <Card className="glass">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-emerald-500/10 p-2">
              <Settings2 className="h-4 w-4 text-emerald-500" />
            </div>
            <CardTitle className="font-heading text-base">Application Info</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <p className="text-muted-foreground text-xs uppercase tracking-wide font-medium mb-1">Application</p>
              <p className="font-semibold">SmartGrader v0.3.0</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs uppercase tracking-wide font-medium mb-1">Project Type</p>
              <p className="font-semibold">Final Year Project (PFE)</p>
            </div>
          </div>
          <div>
            <p className="text-muted-foreground text-xs uppercase tracking-wide font-medium mb-1">Description</p>
            <p>Academic Exam Management System with AI-Powered Grading</p>
          </div>

          <Separator />

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <p className="text-muted-foreground text-xs uppercase tracking-wide font-medium">Tech Stack</p>
              <HelpTooltip text="Technologies powering SmartGrader." />
            </div>
            <div className="flex flex-wrap gap-2 mt-1">
              {TECH_STACK.map((t) => (
                <Badge
                  key={t.name}
                  variant="outline"
                  className={`text-xs px-2.5 py-0.5 ${t.color} cursor-default`}
                >
                  {t.name}
                </Badge>
              ))}
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <p className="text-muted-foreground text-xs uppercase tracking-wide font-medium">Links</p>
            <div className="flex flex-wrap gap-2 mt-1">
              <Link to="/documentation">
                <Button variant="outline" size="sm" className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200 gap-2">
                  <BookOpen className="h-3.5 w-3.5" /> Documentation
                </Button>
              </Link>
              <Link to="/academic-docs">
                <Button variant="outline" size="sm" className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200 gap-2">
                  <ExternalLink className="h-3.5 w-3.5" /> Academic Thesis
                </Button>
              </Link>
              <Link to="/help">
                <Button variant="outline" size="sm" className="cursor-pointer hover:-translate-y-0.5 transition-all duration-200 gap-2">
                  <ArrowRight className="h-3.5 w-3.5" /> Help
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3. Quick Links */}
      <Card className="glass">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-amber-500/10 p-2">
              <ExternalLink className="h-4 w-4 text-amber-500" />
            </div>
            <CardTitle className="font-heading text-base">Quick Links</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            {QUICK_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className="group">
                <div className="glass rounded-xl p-4 flex items-start gap-3 hover:-translate-y-0.5 hover:shadow-md transition-all duration-200 cursor-pointer border border-transparent hover:border-primary/20">
                  <div className={`rounded-lg ${link.color} p-2.5 shrink-0`}>
                    <link.icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm group-hover:text-primary transition-colors">
                      {link.title}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-snug">{link.desc}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground/50 shrink-0 mt-0.5 group-hover:text-primary group-hover:translate-x-0.5 transition-all duration-200" />
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 4. System Status */}
      <Card className="glass">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-violet-500/10 p-2">
              <Server className="h-4 w-4 text-violet-500" />
            </div>
            <CardTitle className="font-heading text-base">System Status</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="glass rounded-xl p-3 space-y-1">
              <div className="flex items-center gap-2 text-xs text-muted-foreground uppercase tracking-wide font-medium">
                <Server className="h-3.5 w-3.5" />
                API Endpoint
              </div>
              <p className="font-mono text-xs break-all">http://localhost:5000</p>
            </div>
            <div className="glass rounded-xl p-3 space-y-1">
              <div className="flex items-center gap-2 text-xs text-muted-foreground uppercase tracking-wide font-medium">
                <Database className="h-3.5 w-3.5" />
                Database
              </div>
              <p className="font-mono text-xs">SQLite</p>
              <p className="text-xs text-muted-foreground">instance/smart_grader.db</p>
            </div>
            <div className="glass rounded-xl p-3 space-y-1">
              <div className="flex items-center gap-2 text-xs text-muted-foreground uppercase tracking-wide font-medium">
                <Brain className="h-3.5 w-3.5" />
                AI Model
              </div>
              <p className="font-mono text-xs">Qwen2.5-VL-3B</p>
              <p className="text-xs text-muted-foreground">Instruct variant</p>
            </div>
          </div>

          <Separator />

          <ApiHealthButton />
        </CardContent>
      </Card>
    </div>
  );
}
