import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useStudentExams() {
  return useQuery({ queryKey: ["student-exams"], queryFn: () => fetchAPI("/student/exams") });
}

export function useStartAttempt() {
  return useMutation({
    mutationFn: (sessionId) => fetchAPI(`/student/exams/${sessionId}/start`, { method: "POST" }),
  });
}

export function useExamStatus(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["student-exams", sessionId, "status"],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/status`),
    enabled: !!sessionId && enabled,
    refetchInterval: 30000,
  });
}

export function useSaveAnswer() {
  return useMutation({
    mutationFn: ({ sessionId, questionId, choiceId }) =>
      fetchAPI(`/student/exams/${sessionId}/answer`, {
        method: "POST",
        body: JSON.stringify({ question_id: questionId, choice_id: choiceId }),
      }),
  });
}

export function useSaveAnswersBatch() {
  return useMutation({
    mutationFn: ({ sessionId, answers }) =>
      fetchAPI(`/student/exams/${sessionId}/answers`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
  });
}

export function useSubmitExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (sessionId) => fetchAPI(`/student/exams/${sessionId}/submit`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["student-exams"] }),
  });
}

export function useExamResult(sessionId) {
  return useQuery({
    queryKey: ["student-exams", sessionId, "result"],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/result`),
    enabled: !!sessionId,
  });
}
