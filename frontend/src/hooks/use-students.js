import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useStudents() {
  return useQuery({
    queryKey: ["students"],
    queryFn: () => fetchAPI("/students"),
  });
}

export function useCreateStudent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) =>
      fetchAPI("/students", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["students"] }),
  });
}
