import "./index.css";
import { Composition } from "remotion";
import { MyComposition } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SmartGraderShowcase"
        component={MyComposition}
        durationInFrames={905}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
