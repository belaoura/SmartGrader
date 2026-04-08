import { useProctorStatus } from "@/hooks/use-proctor";

export default function ProctorWarningBanner({ sessionId, onCaptureRequest }) {
  const { data: status } = useProctorStatus(sessionId);

  if (!status) return null;

  if (status.pending_capture && onCaptureRequest) {
    onCaptureRequest();
  }

  if (status.flagged) {
    return (
      <div className="fixed top-16 left-0 right-0 z-50 bg-destructive/90 text-destructive-foreground text-center py-2 text-sm font-medium">
        Your exam has been flagged for review
      </div>
    );
  }

  if (status.warning_count > 0) {
    return (
      <div className="fixed top-16 left-0 right-0 z-50 bg-yellow-500/90 text-black text-center py-2 text-sm font-medium">
        Suspicious activity detected — Warning {status.warning_count} of {status.warning_threshold}
      </div>
    );
  }

  return null;
}
