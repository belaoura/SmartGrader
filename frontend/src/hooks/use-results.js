import { useQuery } from "@tanstack/react-query";
import { fetchAPI } from "@/lib/api";

export function useExamResults(examId) {
  return useQuery({
    queryKey: ["results", "exam", examId],
    queryFn: () => fetchAPI(`/results/exam/${examId}`),
    enabled: !!examId,
  });
}
