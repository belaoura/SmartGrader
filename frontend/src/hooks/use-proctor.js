import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI, uploadFile } from "@/lib/api";

export function useProctorStatus(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-status", sessionId],
    queryFn: () => fetchAPI(`/student/exams/${sessionId}/proctor/status`),
    enabled: !!sessionId && enabled,
    refetchInterval: 15000,
  });
}

export function useLogEvent() {
  return useMutation({
    mutationFn: ({ sessionId, eventType, severity, details }) =>
      fetchAPI(`/student/exams/${sessionId}/proctor/event`, {
        method: "POST",
        body: JSON.stringify({ event_type: eventType, severity, details }),
      }),
  });
}

export function useUploadSnapshot() {
  return useMutation({
    mutationFn: ({ sessionId, file, snapshotType }) => {
      const formData = new FormData();
      formData.append("file", file, "snapshot.jpg");
      formData.append("snapshot_type", snapshotType);
      return uploadFile(`/student/exams/${sessionId}/proctor/snapshot`, formData);
    },
  });
}

export function useProctorEvents(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-events", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/events`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useProctorSnapshots(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-snapshots", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/snapshots`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useProctorSummary(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["proctor-summary", sessionId],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/proctor/summary`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}

export function useRequestCapture() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, studentId }) =>
      fetchAPI(`/sessions/${sessionId}/proctor/capture/${studentId}`, { method: "POST" }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["proctor-snapshots", sessionId] }),
  });
}

export function useToggleFlag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, attemptId }) =>
      fetchAPI(`/sessions/${sessionId}/proctor/flag/${attemptId}`, { method: "POST" }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["proctor-summary", sessionId] }),
  });
}
