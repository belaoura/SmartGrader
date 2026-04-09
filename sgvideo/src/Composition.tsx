import React from "react";
import { AbsoluteFill, Series } from "remotion";
import { loadFont } from "@remotion/google-fonts/Poppins";

import { Background } from "./components/Background";
import { IntroScene } from "./scenes/IntroScene";
import { FeaturesScene } from "./scenes/FeaturesScene";
import { StatsScene } from "./scenes/StatsScene";
import { ChartScene } from "./scenes/ChartScene";
import { ArchitectureScene } from "./scenes/ArchitectureScene";
import { OutroScene } from "./scenes/OutroScene";

// Load Poppins font (same as webapp)
loadFont("normal", {
  weights: ["400", "500", "600", "700", "800"],
});

// Scene durations in frames (30 fps):
//   Intro: 135 frames (4.5s)
//   Features: 165 frames (5.5s)
//   Stats: 155 frames (~5.2s)
//   Chart: 155 frames (~5.2s)
//   Architecture: 155 frames (~5.2s)
//   Outro: 140 frames (~4.7s)
// Total: 905 frames (~30.2s)

export const MyComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#020617" }}>
      <Background />
      <Series>
        <Series.Sequence durationInFrames={135}>
          <IntroScene />
        </Series.Sequence>
        <Series.Sequence durationInFrames={165}>
          <FeaturesScene />
        </Series.Sequence>
        <Series.Sequence durationInFrames={155}>
          <StatsScene />
        </Series.Sequence>
        <Series.Sequence durationInFrames={155}>
          <ChartScene />
        </Series.Sequence>
        <Series.Sequence durationInFrames={155}>
          <ArchitectureScene />
        </Series.Sequence>
        <Series.Sequence durationInFrames={140}>
          <OutroScene />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
