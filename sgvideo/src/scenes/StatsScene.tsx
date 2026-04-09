import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { IconCheck, IconDatabase, IconCode, IconServer } from "../components/Icons";
import { theme } from "../theme";

type Stat = {
  value: number;
  suffix: string;
  label: string;
  icon: React.FC<{ size?: number; color?: string; strokeWidth?: number }>;
  color: string;
  gradient: string;
};

const stats: Stat[] = [
  {
    value: 191,
    suffix: "",
    label: "Automated Tests",
    icon: IconCheck,
    color: theme.green,
    gradient: "linear-gradient(135deg, #10B981 0%, #34D399 100%)",
  },
  {
    value: 15,
    suffix: "+",
    label: "Database Models",
    icon: IconDatabase,
    color: theme.blue,
    gradient: "linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)",
  },
  {
    value: 40,
    suffix: "+",
    label: "API Endpoints",
    icon: IconCode,
    color: theme.purpleLight,
    gradient: "linear-gradient(135deg, #A855F7 0%, #C084FC 100%)",
  },
  {
    value: 4,
    suffix: "",
    label: "Complete Phases",
    icon: IconServer,
    color: theme.yellow,
    gradient: "linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)",
  },
];

export const StatsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Header
  const headerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const headerY = interpolate(frame, [0, 20], [30, 0], {
    extrapolateRight: "clamp",
  });

  // Scene fade out
  const sceneFade = interpolate(frame, [130, 150], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "80px 120px",
        opacity: sceneFade,
      }}
    >
      {/* Header */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 100,
          opacity: headerOpacity,
          transform: `translateY(${headerY}px)`,
        }}
      >
        <div
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 20,
            color: theme.primary,
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            fontWeight: 600,
            marginBottom: 12,
          }}
        >
          By The Numbers
        </div>
        <h2
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 84,
            fontWeight: 700,
            color: theme.fg,
            margin: 0,
            letterSpacing: "-0.02em",
            background: "linear-gradient(135deg, #ffffff 0%, #A5B4FC 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          Built at Scale
        </h2>
      </div>

      {/* Stats grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 48,
          width: "100%",
          maxWidth: 1600,
        }}
      >
        {stats.map((stat, i) => {
          const cardDelay = 25 + i * 12;
          const cardSpring = spring({
            frame: frame - cardDelay,
            fps,
            config: { damping: 12, stiffness: 100 },
          });
          const cardOpacity = interpolate(
            frame,
            [cardDelay, cardDelay + 15],
            [0, 1],
            { extrapolateRight: "clamp" },
          );

          // Count up animation
          const countProgress = interpolate(
            frame,
            [cardDelay + 5, cardDelay + 40],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          );
          const displayValue = Math.floor(countProgress * stat.value);

          // Icon pulse
          const iconPulse = 1 + Math.sin((frame - cardDelay) / 12) * 0.04;

          const Icon = stat.icon;

          return (
            <div
              key={i}
              style={{
                background: "rgba(15,23,42,0.7)",
                backdropFilter: "blur(20px)",
                border: `1px solid ${theme.border}`,
                borderRadius: 28,
                padding: 44,
                textAlign: "center",
                opacity: cardOpacity,
                transform: `translateY(${(1 - cardSpring) * 60}px) scale(${0.85 + cardSpring * 0.15})`,
                boxShadow: `0 30px 70px rgba(0,0,0,0.5), 0 0 50px ${stat.color}20`,
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Background glow */}
              <div
                style={{
                  position: "absolute",
                  top: -100,
                  right: -100,
                  width: 300,
                  height: 300,
                  borderRadius: "50%",
                  background: `radial-gradient(circle, ${stat.color}25 0%, transparent 70%)`,
                }}
              />

              {/* Icon */}
              <div
                style={{
                  width: 90,
                  height: 90,
                  borderRadius: 22,
                  background: stat.gradient,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 28px",
                  boxShadow: `0 15px 40px ${stat.color}50`,
                  transform: `scale(${iconPulse})`,
                  position: "relative",
                }}
              >
                <Icon size={50} color="white" strokeWidth={2.5} />
              </div>

              {/* Number */}
              <div
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 110,
                  fontWeight: 800,
                  color: theme.fg,
                  lineHeight: 1,
                  letterSpacing: "-0.03em",
                  position: "relative",
                  background: stat.gradient,
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {displayValue}
                {stat.suffix}
              </div>

              {/* Label */}
              <div
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 22,
                  color: theme.fgMuted,
                  marginTop: 16,
                  fontWeight: 500,
                  letterSpacing: "0.01em",
                  position: "relative",
                }}
              >
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
