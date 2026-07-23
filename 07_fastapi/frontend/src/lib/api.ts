import type { Idea, IdeaAnalysis, IdeaInput } from "@/lib/types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail
          ? JSON.stringify(detail)
          : `요청에 실패했습니다. (${response.status})`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getIdeas(): Promise<Idea[]> {
  return request<Idea[]>("/ideas");
}

export function createIdea(payload: IdeaInput): Promise<Idea> {
  return request<Idea>("/ideas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteIdea(ideaId: number): Promise<{ message: string }> {
  return request<{ message: string }>(`/ideas/${ideaId}`, {
    method: "DELETE",
  });
}

export function analyzeIdea(
  ideaId: number,
  force = false,
): Promise<IdeaAnalysis> {
  return request<IdeaAnalysis>(
    `/ideas/${ideaId}/analyze${force ? "?force=true" : ""}`,
    { method: "POST" },
  );
}
