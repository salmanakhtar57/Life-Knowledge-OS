import { useState } from "react";
import { Header } from "./components/Header";
import { QuestionForm } from "./components/QuestionForm";
import { AnswerCard } from "./components/AnswerCard";
import type { AskResponse } from "./types/api";

interface Card {
  id: number;
  question: string;
  response: AskResponse;
}

export default function App() {
  const [cards, setCards] = useState<Card[]>([]);

  function handleAnswered(question: string, response: AskResponse) {
    setCards((prev) => [{ id: Date.now(), question, response }, ...prev]);
  }

  return (
    <main className="page">
      <Header />
      <QuestionForm onAnswered={handleAnswered} />
      {cards.length === 0 ? (
        <p className="empty-state">
          No card yet — ask something above and it'll be filed here.
        </p>
      ) : (
        <div className="card-list">
          {cards.map((card) => (
            <AnswerCard key={card.id} question={card.question} response={card.response} />
          ))}
        </div>
      )}
    </main>
  );
}
