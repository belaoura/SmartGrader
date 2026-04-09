import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { theme } from "../theme";

// Animated bar chart showing project metrics
type BarData = {
  label: string;
  value: number;
  maxValue: number;
  color: string;
  gradient: string;
};

const barsData: BarData[] = [
  { label: "Phase 1: Auth", value: 97, maxValue: 100, color: theme.blue, gradient: "linear-gradient(180deg, #60A5FA 0%, #3B82F6 100%)" },
  { label: "Phase 2: Online Exam", value: 100, maxValue: 100, color: theme.cyan, gradient: "linear-gradient(180deg, #22D3EE 0%, #0EA5E9 100%)" },
  { label: "Phase 3: Anti-Cheat", value: 100, maxValue: 100, color: theme.purpleLight, gradient: "linear-gradient(180deg, #C084FC 0%, #A855F7 100%)" },
  { label: "Phase 4: Deployment", value: 100, maxValue: 100, color: theme.pink, gradient: "linear-gradient(180deg, #F472B6 0%, #DB2777 100%)" },
  { label: "Tests Passing", value: 191, maxValue: 200, color: theme.green, gradient: "linear-gradient(180deg, #34D399 0%, #10B981 100%)" },
  { label: "Documentation", value: 100, maxValue: 100, color: theme.yellow, gradient: "linear-gradient(180deg, #FBBF24 0%, #F59E0B 100%)" },
];

export const ChartScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Header
  const headerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const headerY = interpolate(frame, [0, 20], [30, 0], {
    extrapolateRight: "clamp",
  });

  // Chart container
  const chartOpacity = interpolate(frame, [15, 35], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Scene fade out
  const sceneFade = interpolate(frame, [130, 150], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const maxBarHeight = 420;
  const barWidth = 140;
  const gap = 50;

  return (
    <AbsoluteFill
      style={{
        padding: "80px 120px",
        opacity: sceneFade,
        justifyContent: "center",
      }}
    >
      {/* Header */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 80,
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
          Development Progress
        </div>
        <h2
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 80,
            fontWeight: 700,
            color: theme.fg,
            margin: 0,
            letterSpacing: "-0.02em",
            background: "linear-gradient(135deg, #ffffff 0%, #C4B5FD 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          All Phases Complete
        </h2>
      </div>

      {/* Chart */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-end",
          gap,
          height: maxBarHeight + 120,
          opacity: chartOpacity,
        }}
      >
        {barsData.map((bar, i) => {
          const barDelay = 30 + i * 8;
          const barSpring = spring({
            frame: frame - barDelay,
            fps,
            config: { damping: 14, stiffness: 70 },
          });
          const barHeight = (bar.value / bar.maxValue) * maxBarHeight * barSpring;

          // Count up number
          const countProgress = interpolate(
            frame,
            [barDelay, barDelay + 30],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          );
          const displayValue = Math.floor(countProgress * bar.value);

          // Label fade
          const labelOpacity = interpolate(
            frame,
            [barDelay + 10, barDelay + 30],
            [0, 1],
            { extrapolateRight: "clamp" },
          );

          return (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                position: "relative",
              }}
            >
              {/* Value above bar */}
              <div
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 42,
                  fontWeight: 700,
                  color: bar.color,
                  marginBottom: 16,
                  opacity: labelOpacity,
                  textShadow: `0 0 20px ${bar.color}80`,
                }}
              >
                {displayValue}
                {bar.maxValue === 100 ? "%" : ""}
              </div>

              {/* Bar */}
              <div
                style={{
                  width: barWidth,
                  height: barHeight,
                  background: bar.gradient,
                  borderRadius: "16px 16px 0 0",
                  boxShadow: `0 0 40px ${bar.color}60, inset 0 2px 10px rgba(255,255,255,0.3)`,
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {/* Shine effect */}
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: "30%",
                    background: "linear-gradient(180deg, rgba(255,255,255,0.25) 0%, transparent 100%)",
                  }}
                />
              </div>

              {/* Label below */}
              <div
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 18,
                  fontWeight: 500,
                  color: theme.fgMuted,
                  marginTop: 20,
                  textAlign: "center",
                  maxWidth: barWidth + 30,
                  opacity: labelOpacity,
                  lineHeight: 1.3,
                }}
              >
                {bar.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
