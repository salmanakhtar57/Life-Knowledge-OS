import { SourceTag } from "./SourceTag";
import type { AskResponse } from "../types/api";

interface AnswerCardProps {
  question: string;
  response: AskResponse;
}

export function AnswerCard({ question, response }: AnswerCardProps) {
  const sources = Array.from(
    new Map(response.sources.map((source) => [source.document_title, source])).values(),
  );

  return (
    <article className="answer-card">
      <div className="answer-card-tab" aria-hidden="true" />
      <h2>{question}</h2>
      <hr />
      <p>{response.answer}</p>
      {sources.length > 0 && (
        <div className="answer-card-tags">
          {sources.map((source) => (
            <SourceTag
              key={source.document_title}
              label={source.document_title}
              platform={source.source_platform}
              url={source.document_url}
            />
          ))}
        </div>
      )}
    </article>
  );
}