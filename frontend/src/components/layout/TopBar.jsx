import { Menu, Sun, Moon, Search, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";

function LogoIcon() {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="logo-grad" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#6366F1" />
          <stop offset="100%" stopColor="#818CF8" />
        </linearGradient>
      </defs>
      {/* Brain-like abstract shape */}
      <rect width="28" height="28" rx="8" fill="url(#logo-grad)" />
      {/* Simplified checkmark / brain paths */}
      <path
        d="M8 14.5C8 11.46 10.46 9 13.5 9s5.5 2.46 5.5 5.5c0 1.8-.87 3.4-2.2 4.4"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M11 17.5l2.5 2.5 5-5.5"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

function UserAvatar() {
  return (
    <button
      className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-semibold cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-md"
      style={{ boxShadow: "0 0 0 2px rgba(99,102,241,0.3)" }}
      aria-label="User menu"
      title="SmartGrader Admin"
    >
      SG
    </button>
  );
}

export default function TopBar({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center px-4 gap-3"
      style={{
        background: "var(--color-card)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderBottom: "1px solid var(--color-border)",
        boxShadow: "0 1px 0 rgba(99,102,241,0.08), 0 4px 16px -4px rgba(99,102,241,0.06)",
      }}
    >
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden cursor-pointer shrink-0"
        onClick={onMenuClick}
        aria-label="Open sidebar"
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Logo */}
      <div className="flex items-center gap-2.5 select-none">
        <LogoIcon />
        <span
          className="text-lg font-bold leading-none font-heading text-foreground"
        >
          Smart
          <span className="text-primary">Grader</span>
        </span>
      </div>

      {/* Right side actions */}
      <div className="ml-auto flex items-center gap-1">
        {/* Search placeholder */}
        <Button
          variant="ghost"
          size="icon"
          className="cursor-pointer text-muted-foreground hover:text-foreground"
          aria-label="Search"
          title="Search (coming soon)"
        >
          <Search className="h-4.5 w-4.5" />
        </Button>

        {/* Notifications placeholder */}
        <div className="relative">
          <Button
            variant="ghost"
            size="icon"
            className="cursor-pointer text-muted-foreground hover:text-foreground"
            aria-label="Notifications"
            title="Notifications"
          >
            <Bell className="h-4.5 w-4.5" />
          </Button>
          {/* Notification dot badge */}
          <span
            className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary pointer-events-none"
            style={{ boxShadow: "0 0 4px rgba(99,102,241,0.6)" }}
          />
        </div>

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="cursor-pointer text-muted-foreground hover:text-foreground"
          aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          style={{ transition: "all 200ms ease" }}
        >
          {theme === "light" ? (
            <Moon
              className="h-4.5 w-4.5"
              style={{ transition: "transform 300ms ease" }}
            />
          ) : (
            <Sun
              className="h-4.5 w-4.5"
              style={{ transition: "transform 300ms ease", transform: "rotate(45deg)" }}
            />
          )}
        </Button>

        {/* Separator */}
        <div
          className="mx-1 h-6 w-px bg-border"
        />

        {/* User avatar */}
        <UserAvatar />
      </div>
    </header>
  );
}
