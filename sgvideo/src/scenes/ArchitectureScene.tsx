import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { IconMonitor, IconServer, IconDatabase, IconBrain, IconShield } from "../components/Icons";
import { theme } from "../theme";

// Animated architecture diagram showing layered system
type Layer = {
  title: string;
  subtitle: string;
  icon: React.FC<{ size?: number; color?: string; strokeWidth?: number }>;
  color: string;
  gradient: string;
  items: string[];
};

const layers: Layer[] = [
  {
    title: "Frontend",
    subtitle: "React 19 + Vite",
    icon: IconMonitor,
    color: theme.cyan,
    gradient: "linear-gradient(135deg, #22D3EE 0%, #0EA5E9 100%)",
    items: ["20+ Pages", "React Query", "Tailwind CSS", "TensorFlow.js"],
  },
  {
    title: "Auth & Security",
    subtitle: "JWT + bcrypt",
    icon: IconShield,
    color: theme.purpleLight,
    gradient: "linear-gradient(135deg, #C084FC 0%, #A855F7 100%)",
    items: ["httpOnly Cookies", "Role-Based", "Rate Limiting", "Barcode Login"],
  },
  {
    title: "Flask API",
    subtitle: "40+ Endpoints",
    icon: IconServer,
    color: theme.primary,
    gradient: "linear-gradient(135deg, #818CF8 0%, #6366F1 100%)",
    items: ["10 Blueprints", "Service Layer", "REST", "Flask-Limiter"],
  },
  {
    title: "AI & ML",
    subtitle: "Qwen2.5-VL-3B",
    icon: IconBrain,
    color: theme.pink,
    gradient: "linear-gradient(135deg, #F472B6 0%, #EC4899 100%)",
    items: ["Vision Model", "OCR Pipeline", "RAG Loop", "4-bit Quantized"],
  },
  {
    title: "Database",
    subtitle: "SQLAlchemy ORM",
    icon: IconDatabase,
    color: theme.green,
    gradient: "linear-gradient(135deg, #34D399 0%, #10B981 100%)",
    items: ["15+ Models", "SQLite", "Flask-Migrate", "Cascade Deletes"],
  },
];

export const ArchitectureScene: React.FC = () => {
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
        padding: "70px 100px",
        opacity: sceneFade,
      }}
    >
      {/* Header */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 60,
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
          System Architecture
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
          Full-Stack Platform
        </h2>
      </div>

      {/* Architecture layers */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 24,
          alignItems: "center",
          flex: 1,
          justifyContent: "center",
          maxWidth: 1400,
          margin: "0 auto",
          width: "100%",
        }}
      >
        {layers.map((layer, i) => {
          const layerDelay = 25 + i * 10;
          const layerSpring = spring({
            frame: frame - layerDelay,
            fps,
            config: { damping: 14, stiffness: 90 },
          });
          const layerOpacity = interpolate(
            frame,
            [layerDelay, layerDelay + 20],
            [0, 1],
            { extrapolateRight: "clamp" },
          );

          // Connection arrow (between layers)
          const arrowOpacity = interpolate(
            frame,
            [layerDelay + 10, layerDelay + 25],
            [0, 0.8],
            { extrapolateRight: "clamp" },
          );

          const Icon = layer.icon;

          return (
            <React.Fragment key={i}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 30,
                  width: "100%",
                  padding: 28,
                  background: "rgba(15,23,42,0.75)",
                  backdropFilter: "blur(20px)",
                  border: `1.5px solid ${layer.color}40`,
                  borderRadius: 22,
                  opacity: layerOpacity,
                  transform: `translateX(${(1 - layerSpring) * (i % 2 === 0 ? -100 : 100)}px)`,
                  boxShadow: `0 15px 40px rgba(0,0,0,0.5), 0 0 50px ${layer.color}20`,
                }}
              >
                {/* Icon */}
                <div
                  style={{
                    width: 90,
                    height: 90,
                    borderRadius: 18,
                    background: layer.gradient,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    boxShadow: `0 10px 30px ${layer.color}50`,
                  }}
                >
                  <Icon size={50} color="white" strokeWidth={2.2} />
                </div>

                {/* Title + subtitle */}
                <div style={{ minWidth: 320 }}>
                  <div
                    style={{
                      fontFamily: "'Poppins', sans-serif",
                      fontSize: 32,
                      fontWeight: 700,
                      color: theme.fg,
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {layer.title}
                  </div>
                  <div
                    style={{
                      fontFamily: "'Poppins', sans-serif",
                      fontSize: 18,
                      color: layer.color,
                      fontWeight: 500,
                      marginTop: 4,
                    }}
                  >
                    {layer.subtitle}
                  </div>
                </div>

                {/* Tags */}
                <div
                  style={{
                    display: "flex",
                    gap: 10,
                    flex: 1,
                    flexWrap: "wrap",
                    justifyContent: "flex-end",
                  }}
                >
                  {layer.items.map((item, idx) => {
                    const tagDelay = layerDelay + 10 + idx * 3;
                    const tagOpacity = interpolate(
                      frame,
                      [tagDelay, tagDelay + 15],
                      [0, 1],
                      { extrapolateRight: "clamp" },
                    );
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: "10px 18px",
                          borderRadius: 999,
                          background: `${layer.color}15`,
                          border: `1px solid ${layer.color}30`,
                          fontFamily: "'Poppins', sans-serif",
                          fontSize: 16,
                          color: theme.fg,
                          fontWeight: 500,
                          opacity: tagOpacity,
                        }}
                      >
                        {item}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Connection line (except after last) */}
              {i < layers.length - 1 && (
                <div
                  style={{
                    width: 3,
                    height: 12,
                    background: `linear-gradient(180deg, ${layer.color}, ${layers[i + 1].color})`,
                    borderRadius: 2,
                    opacity: arrowOpacity,
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
