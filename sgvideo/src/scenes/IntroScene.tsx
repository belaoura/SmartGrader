import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { IconGraduation, IconSparkle } from "../components/Icons";
import { theme } from "../theme";

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo scale + fade in
  const logoScale = spring({
    frame: frame - 5,
    fps,
    config: { damping: 10, stiffness: 100, mass: 0.8 },
  });

  const logoOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Title reveal
  const titleY = spring({
    frame: frame - 20,
    fps,
    config: { damping: 15, stiffness: 80 },
  });
  const titleOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Subtitle
  const subtitleOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateRight: "clamp",
  });
  const subtitleY = interpolate(frame, [35, 55], [20, 0], {
    extrapolateRight: "clamp",
  });

  // Tagline
  const taglineOpacity = interpolate(frame, [55, 75], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Outro fade
  const outroFade = interpolate(frame, [110, 130], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Logo glow pulse
  const glowPulse = Math.sin(frame / 10) * 0.15 + 0.85;

  // Sparkles around logo
  const sparkles = [0, 1, 2, 3, 4, 5].map(i => {
    const angle = (i / 6) * Math.PI * 2 + frame / 30;
    const radius = 200 + Math.sin(frame / 15 + i) * 20;
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    const sparkleOpacity = interpolate(frame, [20, 40], [0, 0.7], {
      extrapolateRight: "clamp",
    });
    return { x, y, opacity: sparkleOpacity, delay: i };
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        opacity: outroFade,
      }}
    >
      <div style={{ position: "relative", display: "flex", flexDirection: "column", alignItems: "center" }}>
        {/* Sparkles */}
        {sparkles.map((s, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `calc(50% + ${s.x}px)`,
              top: `calc(50% + ${s.y - 80}px)`,
              opacity: s.opacity,
              transform: `rotate(${frame * 3 + i * 60}deg)`,
              color: theme.primary,
            }}
          >
            <IconSparkle size={20} />
          </div>
        ))}

        {/* Logo */}
        <div
          style={{
            width: 180,
            height: 180,
            borderRadius: 40,
            background: "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: `0 0 ${80 * glowPulse}px ${theme.primaryGlow}, 0 20px 60px rgba(99,102,241,0.4)`,
            transform: `scale(${logoScale})`,
            opacity: logoOpacity,
          }}
        >
          <IconGraduation size={100} color="white" strokeWidth={2} />
        </div>

        {/* Title */}
        <h1
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 140,
            fontWeight: 700,
            color: theme.fg,
            margin: "40px 0 0 0",
            letterSpacing: "-0.02em",
            opacity: titleOpacity,
            transform: `translateY(${(1 - titleY) * 40}px)`,
            background: "linear-gradient(135deg, #ffffff 0%, #C4B5FD 50%, #A5B4FC 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          SmartGrader
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 36,
            fontWeight: 500,
            color: theme.fgMuted,
            margin: "12px 0 0 0",
            opacity: subtitleOpacity,
            transform: `translateY(${subtitleY}px)`,
            letterSpacing: "0.02em",
          }}
        >
          AI-Powered Exam Platform
        </p>

        {/* Tagline with divider */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 20,
            marginTop: 32,
            opacity: taglineOpacity,
          }}
        >
          <div style={{ width: 100, height: 2, background: `linear-gradient(90deg, transparent, ${theme.primary})` }} />
          <span
            style={{
              fontFamily: "'Poppins', sans-serif",
              fontSize: 22,
              color: theme.primary,
              letterSpacing: "0.25em",
              textTransform: "uppercase",
              fontWeight: 600,
            }}
          >
            The Complete Exam System
          </span>
          <div style={{ width: 100, height: 2, background: `linear-gradient(90deg, ${theme.primary}, transparent)` }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
