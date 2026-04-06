import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";

function Placeholder({ title }) {
  return <h2 className="text-2xl font-bold font-heading">{title}</h2>;
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Placeholder title="Dashboard" />} />
        <Route path="/exams" element={<Placeholder title="Exams" />} />
        <Route path="/exams/:id" element={<Placeholder title="Exam Detail" />} />
        <Route path="/scanner" element={<Placeholder title="Scanner" />} />
        <Route path="/students" element={<Placeholder title="Students" />} />
        <Route path="/results" element={<Placeholder title="Results" />} />
        <Route path="/settings" element={<Placeholder title="Settings" />} />
      </Route>
    </Routes>
  );
}
