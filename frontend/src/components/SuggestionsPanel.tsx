
interface SuggestionsPanelProps {
  platform: "substack" | "medium";
}

const suggestions = {
  substack: {
    title: "Suggested for Substack",
    description:
      "You've written about focus, productivity and learning. How about...",
    ideas: [
      "The Art of Deep Work",
      "Lessons from 2 Years as a Developer",
      "Building a Second Brain",
    ],
  },
  medium: {
    title: "Suggested for Medium",
    description: "Explore these ideas when you start publishing on Medium...",
    ideas: [
      "The Power of Consistent Learning",
      "Systems for a Focused Life",
      "AI Tools for Creators",
    ],
  },
};

export function SuggestionsPanel({ platform }: SuggestionsPanelProps) {
  const data = suggestions[platform];

  return (
    <section className={`suggestions-panel ${platform}-suggestions`}>
      <div className="suggestion-heading">
        <span className="bulb-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M9 18h6m-5 3h4m-6-6.5A7 7 0 1 1 16 14.5c-.8.7-1 1.3-1 2h-6c0-.7-.2-1.3-1-2Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>

        <div>
          <h3>{data.title}</h3>
          <p>{data.description}</p>
        </div>
      </div>

      <div className="suggestion-chips">
        {data.ideas.map((idea) => (
          <span className="suggestion-chip" key={idea}>
            {idea}
          </span>
        ))}
      </div>
    </section>
  );
}
