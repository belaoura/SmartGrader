import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

export default function BarcodeScanner({ onScan, onError }) {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (scannerRef.current && isScanning) {
        scannerRef.current.stop().catch(() => {});
      }
    };
  }, [isScanning]);

  const startScanning = async () => {
    try {
      const scanner = new Html5Qrcode("barcode-reader");
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 150 },
        },
        (decodedText) => {
          scanner.stop().then(() => {
            setIsScanning(false);
            onScan(decodedText);
          });
        },
        () => {}
      );

      setIsScanning(true);
    } catch (err) {
      onError?.(err.message || "Camera access denied");
    }
  };

  const stopScanning = () => {
    if (scannerRef.current) {
      scannerRef.current.stop().then(() => setIsScanning(false));
    }
  };

  return (
    <div className="space-y-4">
      <div
        id="barcode-reader"
        ref={containerRef}
        className="w-full rounded-lg overflow-hidden border border-border bg-muted"
        style={{ minHeight: isScanning ? 250 : 0 }}
      />
      {!isScanning ? (
        <button
          type="button"
          onClick={startScanning}
          className="w-full rounded-lg bg-primary px-4 py-3 text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          Start Camera Scan
        </button>
      ) : (
        <button
          type="button"
          onClick={stopScanning}
          className="w-full rounded-lg bg-destructive px-4 py-3 text-destructive-foreground font-medium hover:bg-destructive/90 transition-colors"
        >
          Stop Camera
        </button>
      )}
    </div>
  );
}
