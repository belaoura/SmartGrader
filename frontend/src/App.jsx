import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Exams from "@/pages/Exams";
import ExamDetail from "@/pages/ExamDetail";
import Scanner from "@/pages/Scanner";
import Students from "@/pages/Students";
import Results from "@/pages/Results";
import Settings from "@/pages/Settings";
import Documentation from "@/pages/Documentation";
import AcademicDocs from "@/pages/AcademicDocs";
import AIConfig from "@/pages/AIConfig";
import SampleData from "@/pages/SampleData";
import LegacyCode from "@/pages/LegacyCode";
import Help from "@/pages/Help";

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
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/academic-docs" element={<AcademicDocs />} />
        <Route path="/samples" element={<SampleData />} />
        <Route path="/legacy" element={<LegacyCode />} />
        <Route path="/ai-config" element={<AIConfig />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
