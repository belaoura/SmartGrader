import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useSessions() {
  return useQuery({ queryKey: ["sessions"], queryFn: () => fetchAPI("/sessions") });
}

export function useSession(id) {
  return useQuery({
    queryKey: ["sessions", id],
    queryFn: () => fetchAPI(`/sessions/${id}`),
    enabled: !!id,
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => fetchAPI("/sessions", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useUpdateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => fetchAPI(`/sessions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetchAPI(`/sessions/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useAssignStudents() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, studentIds, groupIds }) =>
      fetchAPI(`/sessions/${sessionId}/assign`, {
        method: "POST",
        body: JSON.stringify({ student_ids: studentIds, group_ids: groupIds }),
      }),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ["sessions", sessionId] }),
  });
}

export function useMonitorSession(sessionId, enabled = true) {
  return useQuery({
    queryKey: ["sessions", sessionId, "monitor"],
    queryFn: () => fetchAPI(`/sessions/${sessionId}/monitor`),
    enabled: !!sessionId && enabled,
    refetchInterval: 10000,
  });
}
