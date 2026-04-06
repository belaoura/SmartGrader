import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchAPI, uploadFile } from "@/lib/api";

export function useAIStatus() {
  return useQuery({
    queryKey: ["ai", "status"],
    queryFn: () => fetchAPI("/ai/status"),
    refetchInterval: 30000,
  });
}

export function useOCR() {
  return useMutation({
    mutationFn: ({ file, questionIds }) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("question_ids", JSON.stringify(questionIds));
      return uploadFile("/ai/ocr", formData);
    },
  });
}

export function useEvaluate() {
  return useMutation({
    mutationFn: (data) =>
      fetchAPI("/ai/evaluate", { method: "POST", body: JSON.stringify(data) }),
  });
}

export function useCorrect() {
  return useMutation({
    mutationFn: (data) =>
      fetchAPI("/ai/correct", { method: "POST", body: JSON.stringify(data) }),
  });
}
