import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import {
  IconBook,
  IconScan,
  IconBrain,
  IconMonitor,
  IconEye,
  IconChart,
} from "../components/Icons";
import { theme } from "../theme";

type Feature = {
  icon: React.FC<{ size?: number; color?: string; strokeWidth?: number }>;
  title: string;
  desc: string;
  color: string;
  gradient: string;
};

const features: Feature[] = [
  {
    icon: IconBook,
    title: "Exam Management",
    desc: "Create MCQ exams with printable answer sheets",
    color: theme.blue,
    gradient: "linear-gradient(135deg, #60A5FA 0%, #818CF8 100%)",
  },
  {
    icon: IconScan,
    title: "OMR Scanning",
    desc: "OpenCV auto-grades filled bubble sheets",
    color: theme.cyan,
    gradient: "linear-gradient(135deg, #22D3EE 0%, #60A5FA 100%)",
  },
  {
    icon: IconBrain,
    title: "AI Grading",
    desc: "Qwen2.5-VL evaluates handwritten answers",
    color: theme.purpleLight,
    gradient: "linear-gradient(135deg, #C084FC 0%, #A855F7 100%)",
  },
  {
    icon: IconMonitor,
    title: "Online Exams",
    desc: "Browser-based with timer & auto-save",
    color: theme.greenLight,
    gradient: "linear-gradient(135deg, #34D399 0%, #22D3EE 100%)",
  },
  {
    icon: IconEye,
    title: "Anti-Cheat Proctoring",
    desc: "Face detection & event tracking",
    color: theme.pink,
    gradient: "linear-gradient(135deg, #F472B6 0%, #A855F7 100%)",
  },
  {
    icon: IconChart,
    title: "Analytics Dashboard",
    desc: "Real-time stats & exportable reports",
    color: theme.yellow,
    gradient: "linear-gradient(135deg, #FBBF24 0%, #FB923C 100%)",
  },
];

export const FeaturesScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Header animation
  const headerSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 15, stiffness: 80 },
  });
  const headerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out at end
  const sceneFade = interpolate(frame, [140, 160], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        padding: "80px 120px",
        opacity: sceneFade,
      }}
    >
      {/* Header */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 80,
          opacity: headerOpacity,
          transform: `translateY(${(1 - headerSpring) * 30}px)`,
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
          Core Features
        </div>
        <h2
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontSize: 84,
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
          Everything You Need
        </h2>
      </div>

      {/* Feature grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 40,
          flex: 1,
          alignContent: "center",
        }}
      >
        {features.map((feature, i) => {
          // Stagger entry per card
          const cardDelay = 25 + i * 10;
          const cardSpring = spring({
            frame: frame - cardDelay,
            fps,
            config: { damping: 12, stiffness: 90 },
          });
          const cardOpacity = interpolate(
            frame,
            [cardDelay, cardDelay + 20],
            [0, 1],
            { extrapolateRight: "clamp" },
          );

          // Icon pulse
          const iconScale = 1 + Math.sin((frame - cardDelay) / 15) * 0.03;

          const Icon = feature.icon;

          return (
            <div
              key={i}
              style={{
                background: "rgba(15,23,42,0.6)",
                backdropFilter: "blur(20px)",
                border: `1px solid ${theme.border}`,
                borderRadius: 24,
                padding: 36,
                opacity: cardOpacity,
                transform: `translateY(${(1 - cardSpring) * 50}px) scale(${0.9 + cardSpring * 0.1})`,
                boxShadow: `0 20px 60px rgba(0,0,0,0.4), 0 0 40px ${feature.color}15`,
              }}
            >
              <div
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: 20,
                  background: feature.gradient,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: 24,
                  boxShadow: `0 10px 30px ${feature.color}40`,
                  transform: `scale(${iconScale})`,
                }}
              >
                <Icon size={44} color="white" strokeWidth={2.2} />
              </div>
              <h3
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 32,
                  fontWeight: 600,
                  color: theme.fg,
                  margin: "0 0 10px 0",
                  letterSpacing: "-0.01em",
                }}
              >
                {feature.title}
              </h3>
              <p
                style={{
                  fontFamily: "'Poppins', sans-serif",
                  fontSize: 19,
                  color: theme.fgMuted,
                  margin: 0,
                  lineHeight: 1.5,
                  fontWeight: 400,
                }}
              >
                {feature.desc}
              </p>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
