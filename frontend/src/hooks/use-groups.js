import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useGroups() {
  return useQuery({ queryKey: ["groups"], queryFn: () => fetchAPI("/groups") });
}

export function useGroup(id) {
  return useQuery({
    queryKey: ["groups", id],
    queryFn: () => fetchAPI(`/groups/${id}`),
    enabled: !!id,
  });
}

export function useCreateGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => fetchAPI("/groups", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useDeleteGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => fetchAPI(`/groups/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useAddMembers() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, studentIds }) =>
      fetchAPI(`/groups/${groupId}/members`, { method: "POST", body: JSON.stringify({ student_ids: studentIds }) }),
    onSuccess: (_, { groupId }) => qc.invalidateQueries({ queryKey: ["groups", groupId] }),
  });
}

export function useRemoveMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, studentId }) =>
      fetchAPI(`/groups/${groupId}/members/${studentId}`, { method: "DELETE" }),
    onSuccess: (_, { groupId }) => qc.invalidateQueries({ queryKey: ["groups", groupId] }),
  });
}
