import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Exams from "@/pages/Exams";
import ExamDetail from "@/pages/ExamDetail";
import Scanner from "@/pages/Scanner";

function Placeholder({ title }) {
  return <h2 className="text-2xl font-bold font-heading">{title}</h2>;
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/exams" element={<Exams />} />
        <Route path="/exams/:id" element={<ExamDetail />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/students" element={<Placeholder title="Students" />} />
        <Route path="/results" element={<Placeholder title="Results" />} />
        <Route path="/settings" element={<Placeholder title="Settings" />} />
      </Route>
    </Routes>
  );
}
