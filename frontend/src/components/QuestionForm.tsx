import { useState, type FormEvent } from "react";
import { askQuestion, ApiError } from "../api/client";
import type { AskResponse } from "../types/api";

interface QuestionFormProps {
  onAnswered: (question: string, response: AskResponse) => void;
}

export function QuestionForm({ onAnswered }: QuestionFormProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    try {
      const response = await askQuestion(trimmed);
      onAnswered(trimmed, response);
      setQuestion("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <div className="question-form-tab" aria-hidden="true" />
      <label htmlFor="question-input" className="question-form-label">
        New card
      </label>
      <div className="question-form-row">
        <input
          id="question-input"
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="What did I write about deep work?"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Filing..." : "File it"}
        </button>
      </div>
      {error && <p className="question-form-error">{error}</p>}
    </form>
  );
}
