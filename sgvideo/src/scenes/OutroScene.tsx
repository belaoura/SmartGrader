import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { IconGraduation, IconRocket, IconCheck } from "../components/Icons";
import { theme } from "../theme";

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo entry
  const logoScale = spring({
    frame: frame - 5,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Text entries
  const mainTextOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: "clamp",
  });
  const mainTextY = interpolate(frame, [20, 40], [30, 0], {
    extrapolateRight: "clamp",
  });

  const subTextOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateRight: "clamp",
  });

  const ctaOpacity = interpolate(frame, [50, 70], [0, 1], {
    extrapolateRight: "clamp",
  });
  const ctaScale = spring({
    frame: frame - 50,
    fps,
    config: { damping: 10, stiffness: 120 },
  });

  const badgesOpacity = interpolate(frame, [65, 85], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Final fade
  const finalFade = interpolate(frame, [115, 135], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Logo pulse
  const pulse = Math.sin(frame / 10) * 0.1 + 0.9;

  // Radiating circles behind logo
  const rings = [0, 1, 2].map(i => {
    const ringProgress = ((frame + i * 20) % 60) / 60;
    const ringScale = 0.5 + ringProgress * 2;
    const ringOpacity = (1 - ringProgress) * 0.4;
    return { scale: ringScale, opacity: ringOpacity };
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        opacity: finalFade,
      }}
    >
      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Radiating rings */}
        {rings.map((ring, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              top: -40,
              width: 200,
              height: 200,
              borderRadius: "50%",
              border: `2px solid ${theme.primary}`,
              opacity: ring.opacity * logoOpacity,
              transform: `scale(${ring.scale})`,
            }}
          />
        ))}

        {/* Logo */}
        <div
          style={{
            width: 200,
            height: 200,
            borderRadius: 44,
            background: "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: `0 0 120px ${theme.primaryGlow}, 0 30px 80px rgba(99,102,241,0.5)`,
            transform: `scale(${logoScale * pulse})`,
            opacity: logoOpacity,
            marginBottom: 50,
          }}
        >
          <IconGraduation size={110} color="white" strokeWidth={2} />
        </div>

        {/* Main text */}
        <h1
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 110,
            fontWeight: 800,
            color: theme.fg,
            margin: 0,
            letterSpacing: "-0.03em",
            opacity: mainTextOpacity,
            transform: `translateY(${mainTextY}px)`,
            textAlign: "center",
            background: "linear-gradient(135deg, #ffffff 0%, #C4B5FD 50%, #A5B4FC 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            lineHeight: 1.1,
          }}
        >
          Ready for the Future
          <br />
          of Examinations
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 30,
            fontWeight: 400,
            color: theme.fgMuted,
            margin: "32px 0 0 0",
            letterSpacing: "0.01em",
            opacity: subTextOpacity,
            textAlign: "center",
          }}
        >
          Open source &bull; Academic project &bull; Built with ♥
        </p>

        {/* Version badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginTop: 50,
            padding: "18px 40px",
            borderRadius: 999,
            background: "linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(168,85,247,0.25) 100%)",
            border: `2px solid ${theme.primary}60`,
            backdropFilter: "blur(20px)",
            opacity: ctaOpacity,
            transform: `scale(${0.8 + ctaScale * 0.2})`,
            boxShadow: `0 20px 60px ${theme.primary}40`,
          }}
        >
          <div style={{ color: theme.primary, display: "flex", alignItems: "center" }}>
            <IconRocket size={32} strokeWidth={2.5} />
          </div>
          <span
            style={{
              fontFamily: "'Poppins', sans-serif",
              fontSize: 32,
              fontWeight: 700,
              color: theme.fg,
              letterSpacing: "0.02em",
            }}
          >
            SmartGrader v1.0.0
          </span>
        </div>

        {/* Feature badges */}
        <div
          style={{
            display: "flex",
            gap: 20,
            marginTop: 40,
            opacity: badgesOpacity,
          }}
        >
          {[
            { text: "4 Phases", color: theme.blue },
            { text: "191 Tests", color: theme.green },
            { text: "Production Ready", color: theme.purpleLight },
          ].map((badge, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "12px 24px",
                borderRadius: 999,
                background: "rgba(15,23,42,0.8)",
                border: `1.5px solid ${badge.color}50`,
                backdropFilter: "blur(15px)",
              }}
            >
              <div style={{ color: badge.color }}>
                <IconCheck size={22} strokeWidth={3} />
              </div>
              <span
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 22,
                  fontWeight: 600,
                  color: theme.fg,
                }}
              >
                {badge.text}
              </span>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
