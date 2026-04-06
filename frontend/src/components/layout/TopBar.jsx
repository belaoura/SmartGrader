import { Menu, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";

export default function TopBar({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center border-b border-border bg-card px-4">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden cursor-pointer"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
      </Button>

      <h1 className="ml-2 text-xl font-semibold font-heading lg:ml-0">
        SmartGrader
      </h1>

      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="cursor-pointer"
        >
          {theme === "light" ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  );
}
