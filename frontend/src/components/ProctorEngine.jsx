import { useEffect, useRef, useCallback } from "react";
import { useLogEvent, useUploadSnapshot } from "@/hooks/use-proctor";

// Singleton model load promise
let modelPromise = null;

async function loadBlazeFace() {
  if (!modelPromise) {
    const blazeface = await import("@tensorflow-models/blazeface");
    // Ensure TF.js backend is ready
    await import("@tensorflow/tfjs");
    modelPromise = blazeface.load();
  }
  return modelPromise;
}

export default function ProctorEngine({ sessionId, onError }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const modelRef = useRef(null);
  const detectIntervalRef = useRef(null);
  const snapshotIntervalRef = useRef(null);
  const lastEmitRef = useRef({}); // event_type -> timestamp
  const gazeAwayCountRef = useRef(0);

  const logEvent = useLogEvent();
  const uploadSnapshot = useUploadSnapshot();

  // ── helpers ──────────────────────────────────────────────────────────────

  const shouldEmit = useCallback((eventType) => {
    const now = Date.now();
    const last = lastEmitRef.current[eventType] || 0;
    if (now - last < 10000) return false; // throttle 10s
    lastEmitRef.current[eventType] = now;
    return true;
  }, []);

  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    if (!video || video.readyState < 2) return null;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 320;
    canvas.height = video.videoHeight || 240;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas;
  }, []);

  const captureAndUpload = useCallback(
    (snapshotType) => {
      const canvas = captureFrame();
      if (!canvas) return;
      canvas.toBlob(
        (blob) => {
          if (!blob) return;
          uploadSnapshot.mutate({ sessionId, file: blob, snapshotType });
        },
        "image/jpeg",
        0.7
      );
    },
    [captureFrame, sessionId, uploadSnapshot]
  );

  const emitEvent = useCallback(
    (eventType, severity, details = {}) => {
      if (!shouldEmit(eventType)) return;
      logEvent.mutate({ sessionId, eventType, severity, details });
      // Upload snapshot for medium+ severity
      if (severity === "medium" || severity === "high") {
        captureAndUpload("event_triggered");
      }
    },
    [shouldEmit, logEvent, sessionId, captureAndUpload]
  );

  // ── DOM event listeners ───────────────────────────────────────────────────

  useEffect(() => {
    if (!sessionId) return;

    const handleVisibility = () => {
      if (document.hidden) emitEvent("tab_switch", "high");
    };
    const handleBlur = () => emitEvent("focus_lost", "medium");
    const handleCopy = () => emitEvent("copy_paste", "medium", { action: "copy" });
    const handleCut = () => emitEvent("copy_paste", "medium", { action: "cut" });
    const handlePaste = () => emitEvent("copy_paste", "medium", { action: "paste" });
    const handleContextMenu = (e) => {
      e.preventDefault();
      emitEvent("right_click", "low");
    };
    const handleKeyDown = (e) => {
      const isCtrl = e.ctrlKey || e.metaKey;
      if (
        (isCtrl && ["c", "v", "a", "x"].includes(e.key.toLowerCase())) ||
        e.key === "PrintScreen"
      ) {
        emitEvent("keyboard_shortcut", "medium", { key: e.key });
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("blur", handleBlur);
    document.addEventListener("copy", handleCopy);
    document.addEventListener("cut", handleCut);
    document.addEventListener("paste", handlePaste);
    document.addEventListener("contextmenu", handleContextMenu);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("blur", handleBlur);
      document.removeEventListener("copy", handleCopy);
      document.removeEventListener("cut", handleCut);
      document.removeEventListener("paste", handlePaste);
      document.removeEventListener("contextmenu", handleContextMenu);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [sessionId, emitEvent]);

  // ── Camera + face detection ───────────────────────────────────────────────

  useEffect(() => {
    if (!sessionId) return;

    let cancelled = false;

    async function init() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        const model = await loadBlazeFace();
        if (cancelled) return;
        modelRef.current = model;

        // Face detection every 2s
        detectIntervalRef.current = setInterval(async () => {
          const video = videoRef.current;
          if (!video || video.readyState < 2 || !modelRef.current) return;
          try {
            const predictions = await modelRef.current.estimateFaces(video, false);
            if (predictions.length === 0) {
              gazeAwayCountRef.current = 0;
              emitEvent("no_face", "high");
            } else if (predictions.length >= 2) {
              gazeAwayCountRef.current = 0;
              emitEvent("multiple_faces", "high");
            } else {
              // Single face — basic gaze check via landmark position
              const face = predictions[0];
              const landmarks = face.landmarks; // [[x,y], ...]
              if (landmarks && landmarks.length >= 2) {
                const [leftEye, rightEye] = landmarks;
                const faceWidth = face.bottomRight[0] - face.topLeft[0];
                const faceCenterX = (face.topLeft[0] + face.bottomRight[0]) / 2;
                const videoW = video.videoWidth || 320;
                const offsetRatio = Math.abs(faceCenterX - videoW / 2) / (faceWidth || 1);
                if (offsetRatio > 0.5) {
                  gazeAwayCountRef.current += 1;
                } else {
                  gazeAwayCountRef.current = 0;
                }
                if (gazeAwayCountRef.current >= 5) {
                  gazeAwayCountRef.current = 0;
                  emitEvent("gaze_away", "medium");
                }
              }
            }
          } catch {
            // Ignore detection errors silently
          }
        }, 2000);

        // Periodic snapshot every 60s
        snapshotIntervalRef.current = setInterval(() => {
          captureAndUpload("periodic");
        }, 60000);
      } catch (err) {
        if (!cancelled) {
          onError?.("Camera access denied or unavailable. Proctoring requires camera access.");
        }
      }
    }

    init();

    return () => {
      cancelled = true;
      clearInterval(detectIntervalRef.current);
      clearInterval(snapshotIntervalRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      style={{ position: "fixed", top: -9999, left: -9999, width: 320, height: 240 }}
    />
  );
}
