import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Exams from "@/pages/Exams";
import ExamDetail from "@/pages/ExamDetail";
import Scanner from "@/pages/Scanner";
import Students from "@/pages/Students";
import Results from "@/pages/Results";
import Settings from "@/pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/exams" element={<Exams />} />
        <Route path="/exams/:id" element={<ExamDetail />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/students" element={<Students />} />
        <Route path="/results" element={<Results />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
