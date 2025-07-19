import "./styles.css";
import { useRive, Layout, Fit, Alignment } from "@rive-app/react-webgl2";

export const RiveDemo = () => {
  const { RiveComponent } = useRive({
    // Load a local riv `clean_the_car.riv` or upload your own!
    src: "bunny.riv",
    // Be sure to specify the correct state machine (or animation) name
    stateMachines: "State Machine 1",
    // This is optional.Provides additional layout control.
    layout: new Layout({
      fit: Fit.FitWidth, // Change to: rive.Fit.Contain, or Cover
      alignment: Alignment.Center,
    }),
    autoplay: true,
  });

  return <RiveComponent />;
};

export default function App() {
  return (
    <div className="RiveContainer">
      <RiveDemo></RiveDemo>
    </div>
  );
}
