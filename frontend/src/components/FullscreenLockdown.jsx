import { useEffect, useState, useCallback } from "react";

export default function FullscreenLockdown({ onViolation }) {
  const [exited, setExited] = useState(false);

  useEffect(() => {
    document.documentElement.requestFullscreen?.().catch(() => {});
    const handleChange = () => {
      if (!document.fullscreenElement) {
        setExited(true);
        onViolation?.();
      } else {
        setExited(false);
      }
    };
    document.addEventListener("fullscreenchange", handleChange);
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, [onViolation]);

  const reenter = useCallback(() => {
    document.documentElement.requestFullscreen?.().catch(() => {});
  }, []);

  if (!exited) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="text-xl font-bold text-white">Full-Screen Required</div>
        <p className="text-muted-foreground">Please return to full-screen mode to continue your exam.</p>
        <button
          onClick={reenter}
          className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          Re-enter Full Screen
        </button>
      </div>
    </div>
  );
}
