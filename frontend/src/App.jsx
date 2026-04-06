import { Routes, Route } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="flex min-h-screen items-center justify-center">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold font-heading">SmartGrader</h1>
              <p className="text-muted-foreground">Academic Exam Management System</p>
              <Button>Get Started</Button>
            </div>
          </div>
        }
      />
    </Routes>
  );
}
