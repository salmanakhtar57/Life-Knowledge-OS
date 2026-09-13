import { SourceTag } from "./SourceTag";
import type { AskResponse } from "../types/api";

interface AnswerCardProps {
  question: string;
  response: AskResponse;
}

export function AnswerCard({ question, response }: AnswerCardProps) {
  const sourceLabels = Array.from(
    new Set(response.sources.map((source) => source.document_title)),
  );

  return (
    <article className="answer-card">
      <div className="answer-card-tab" aria-hidden="true" />
      <h2>{question}</h2>
      <hr />
      <p>{response.answer}</p>
      {sourceLabels.length > 0 && (
        <div className="answer-card-tags">
          {sourceLabels.map((label) => (
            <SourceTag key={label} label={label} />
          ))}
        </div>
      )}
    </article>
  );
}
