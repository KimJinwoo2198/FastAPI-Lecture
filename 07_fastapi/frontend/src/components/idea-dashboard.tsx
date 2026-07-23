"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

import { analyzeIdea, createIdea, deleteIdea, getIdeas } from "@/lib/api";
import type { Idea, IdeaAnalysis } from "@/lib/types";

const initialForm = {
  title: "",
  description: "",
  teamSize: "1",
  tags: "",
};

export function IdeaDashboard() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [analyses, setAnalyses] = useState<Record<number, IdeaAnalysis>>({});
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadIdeas = useCallback(async () => {
    try {
      setError("");
      setIdeas(await getIdeas());
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    getIdeas()
      .then((data) => {
        if (!cancelled) setIdeas(data);
      })
      .catch((requestError: unknown) => {
        if (!cancelled) setError(getErrorMessage(requestError));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await createIdea({
        title: form.title,
        description: form.description,
        team_size: Number(form.teamSize),
        tags: form.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      });
      setForm(initialForm);
      await loadIdeas();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAnalyze(ideaId: number, force = false) {
    setAnalyzingId(ideaId);
    setError("");

    try {
      const analysis = await analyzeIdea(ideaId, force);
      setAnalyses((current) => ({ ...current, [ideaId]: analysis }));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setAnalyzingId(null);
    }
  }

  async function handleDelete(ideaId: number) {
    if (!window.confirm("이 아이디어를 삭제할까요?")) return;

    setDeletingId(ideaId);
    setError("");

    try {
      await deleteIdea(ideaId);
      setIdeas((current) => current.filter((idea) => idea.id !== ideaId));
      setAnalyses((current) => {
        const next = { ...current };
        delete next[ideaId];
        return next;
      });
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FASTAPI × UPSTAGE</p>
          <h1>Hackathon Idea Coach</h1>
          <p className="hero-copy">
            아이디어를 기록하고, AI 멘토에게 2일 MVP 범위를 피드백 받으세요.
          </p>
        </div>
        <div className="status-badge">
          <span /> API CONNECTED
        </div>
      </header>

      {error && (
        <div className="error-banner" role="alert">
          <strong>요청을 처리하지 못했습니다.</strong>
          <span>{error}</span>
        </div>
      )}

      <section className="workspace">
        <form className="idea-form" onSubmit={handleSubmit}>
          <div className="section-heading">
            <p>NEW IDEA</p>
            <h2>아이디어 등록</h2>
          </div>

          <label>
            아이디어 이름
            <input
              required
              minLength={2}
              maxLength={50}
              placeholder="예: AI 해커톤 팀 매칭"
              value={form.title}
              onChange={(event) =>
                setForm({ ...form, title: event.target.value })
              }
            />
          </label>

          <label>
            해결하려는 문제
            <textarea
              required
              minLength={10}
              maxLength={500}
              rows={5}
              placeholder="누구의 어떤 문제를 해결하는지 적어주세요."
              value={form.description}
              onChange={(event) =>
                setForm({ ...form, description: event.target.value })
              }
            />
          </label>

          <div className="form-row">
            <label>
              팀원 수
              <input
                required
                type="number"
                min={1}
                max={10}
                value={form.teamSize}
                onChange={(event) =>
                  setForm({ ...form, teamSize: event.target.value })
                }
              />
            </label>
            <label>
              태그
              <input
                placeholder="AI, 교육, 생산성"
                value={form.tags}
                onChange={(event) =>
                  setForm({ ...form, tags: event.target.value })
                }
              />
            </label>
          </div>

          <button className="primary-button" disabled={submitting} type="submit">
            {submitting ? "등록 중..." : "아이디어 등록"}
          </button>
        </form>

        <section className="idea-section">
          <div className="list-heading">
            <div className="section-heading">
              <p>IDEA BOARD</p>
              <h2>등록된 아이디어</h2>
            </div>
            <span>{ideas.length} IDEAS</span>
          </div>

          {loading ? (
            <div className="empty-state">아이디어를 불러오고 있습니다...</div>
          ) : ideas.length === 0 ? (
            <div className="empty-state">
              첫 번째 아이디어를 등록해보세요.
            </div>
          ) : (
            <div className="idea-list">
              {ideas.map((idea) => {
                const analysis = analyses[idea.id];
                const isAnalyzing = analyzingId === idea.id;

                return (
                  <article className="idea-card" key={idea.id}>
                    <div className="card-topline">
                      <span>IDEA #{String(idea.id).padStart(2, "0")}</span>
                      <span>{idea.team_size} PERSON TEAM</span>
                    </div>
                    <h3>{idea.title}</h3>
                    <p className="description">{idea.description}</p>

                    <div className="tag-list">
                      {idea.tags.length ? (
                        idea.tags.map((tag) => <span key={tag}>#{tag}</span>)
                      ) : (
                        <span>#태그없음</span>
                      )}
                    </div>

                    <div className="card-actions">
                      <button
                        className="analyze-button"
                        disabled={isAnalyzing}
                        onClick={() => void handleAnalyze(idea.id)}
                        type="button"
                      >
                        {isAnalyzing ? "AI 분석 중..." : "AI 분석하기"}
                      </button>
                      {analysis && (
                        <button
                          className="ghost-button"
                          disabled={isAnalyzing}
                          onClick={() => void handleAnalyze(idea.id, true)}
                          type="button"
                        >
                          다시 분석
                        </button>
                      )}
                      <button
                        className="delete-button"
                        disabled={deletingId === idea.id}
                        onClick={() => void handleDelete(idea.id)}
                        type="button"
                      >
                        {deletingId === idea.id ? "삭제 중" : "삭제"}
                      </button>
                    </div>

                    {analysis && (
                      <div className="analysis-panel">
                        <div className="analysis-meta">
                          <strong>AI MENTOR REVIEW</strong>
                          <span>
                            {analysis.model} · {analysis.prompt_tokens + analysis.completion_tokens} tokens
                          </span>
                        </div>
                        <div className="markdown">
                          <ReactMarkdown>{analysis.analysis}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
}
