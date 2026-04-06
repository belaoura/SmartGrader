import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useExams() {
  return useQuery({
    queryKey: ["exams"],
    queryFn: () => fetchAPI("/exams"),
  });
}

export function useExam(examId) {
  return useQuery({
    queryKey: ["exams", examId],
    queryFn: () => fetchAPI(`/exams/${examId}`),
    enabled: !!examId,
  });
}

export function useExamQuestions(examId) {
  return useQuery({
    queryKey: ["exams", examId, "questions"],
    queryFn: () => fetchAPI(`/exams/${examId}/questions`),
    enabled: !!examId,
  });
}

export function useCreateExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) =>
      fetchAPI("/exams", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["exams"] }),
  });
}

export function useUpdateExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) =>
      fetchAPI(`/exams/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["exams"] }),
  });
}

export function useDeleteExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetchAPI(`/exams/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["exams"] }),
  });
}

export function useCreateQuestion(examId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) =>
      fetchAPI(`/exams/${examId}/questions`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["exams", examId, "questions"] }),
  });
}
