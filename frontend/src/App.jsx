import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import StudentLayout from "@/components/layout/StudentLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
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
import TeacherManagement from "@/pages/TeacherManagement";
import StudentImport from "@/pages/StudentImport";
import StudentGroups from "@/pages/StudentGroups";
import ExamSessions from "@/pages/ExamSessions";
import CreateSession from "@/pages/CreateSession";
import SessionDetail from "@/pages/SessionDetail";
import StudentDashboard from "@/pages/StudentDashboard";
import TakeExam from "@/pages/TakeExam";
import ExamResult from "@/pages/ExamResult";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Teacher routes */}
      <Route element={<ProtectedRoute role="teacher" />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exams" element={<Exams />} />
          <Route path="/exams/:id" element={<ExamDetail />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/students" element={<Students />} />
          <Route path="/results" element={<Results />} />
          <Route path="/groups" element={<StudentGroups />} />
          <Route path="/sessions" element={<ExamSessions />} />
          <Route path="/sessions/new" element={<CreateSession />} />
          <Route path="/sessions/:id" element={<SessionDetail />} />
          <Route path="/documentation" element={<Documentation />} />
          <Route path="/academic-docs" element={<AcademicDocs />} />
          <Route path="/samples" element={<SampleData />} />
          <Route path="/legacy" element={<LegacyCode />} />
          <Route path="/ai-config" element={<AIConfig />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
        </Route>
      </Route>

      {/* Admin routes */}
      <Route element={<ProtectedRoute role="teacher" requireAdmin />}>
        <Route element={<AppLayout />}>
          <Route path="/admin/teachers" element={<TeacherManagement />} />
          <Route path="/admin/import" element={<StudentImport />} />
        </Route>
      </Route>

      {/* Student routes */}
      <Route element={<ProtectedRoute role="student" />}>
        <Route element={<StudentLayout />}>
          <Route path="/exam" element={<StudentDashboard />} />
          <Route path="/exam/:sessionId" element={<TakeExam />} />
          <Route path="/exam/:sessionId/result" element={<ExamResult />} />
        </Route>
      </Route>
    </Routes>
  );
}
