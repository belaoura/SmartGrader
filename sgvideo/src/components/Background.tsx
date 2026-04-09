import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { theme } from "../theme";

// Animated gradient background with floating orbs and grid
export const Background: React.FC = () => {
  const frame = useCurrentFrame();

  // Animated orb positions (slow floating)
  const orb1X = interpolate(
    Math.sin(frame / 60),
    [-1, 1],
    [-100, 100],
  );
  const orb1Y = interpolate(
    Math.cos(frame / 80),
    [-1, 1],
    [-50, 50],
  );
  const orb2X = interpolate(
    Math.cos(frame / 70),
    [-1, 1],
    [-80, 80],
  );
  const orb2Y = interpolate(
    Math.sin(frame / 50),
    [-1, 1],
    [-60, 60],
  );

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, #0F0B1F 0%, #1E1B4B 50%, #1E1145 100%)`,
      }}
    >
      {/* Orb 1 — indigo */}
      <div
        style={{
          position: "absolute",
          top: `calc(10% + ${orb1Y}px)`,
          left: `calc(5% + ${orb1X}px)`,
          width: 900,
          height: 900,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(99,102,241,0.35) 0%, transparent 65%)",
          filter: "blur(80px)",
        }}
      />

      {/* Orb 2 — purple */}
      <div
        style={{
          position: "absolute",
          bottom: `calc(5% + ${orb2Y}px)`,
          right: `calc(5% + ${orb2X}px)`,
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(168,85,247,0.30) 0%, transparent 65%)",
          filter: "blur(80px)",
        }}
      />

      {/* Orb 3 — blue */}
      <div
        style={{
          position: "absolute",
          top: "40%",
          left: "45%",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(96,165,250,0.20) 0%, transparent 65%)",
          filter: "blur(100px)",
        }}
      />

      {/* Grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.06,
          backgroundImage: `linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
        }}
      />

      {/* Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.5) 100%)",
        }}
      />

      {/* Floating particles */}
      {[...Array(30)].map((_, i) => {
        const speed = 0.5 + (i % 5) * 0.2;
        const seed = i * 37;
        const y = interpolate(
          (frame * speed + seed) % 200,
          [0, 200],
          [1080 + 20, -20],
        );
        const x = 50 + ((seed * 13) % 1820);
        const size = 2 + (i % 3);
        const opacity = 0.3 + (i % 4) * 0.15;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: theme.primary,
              opacity,
              boxShadow: `0 0 ${size * 3}px ${theme.primary}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
