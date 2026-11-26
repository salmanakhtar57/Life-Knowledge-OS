
import json

from sqlalchemy.orm import Session

from app.models import models
from app.schemas.schemas import WritingIdeasResponse
from app.services.generation import generate_answer


def get_writing_ideas(db: Session) -> WritingIdeasResponse:
    articles = (
        db.query(models.Document)
        .join(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.SUBSTACK)
        .order_by(models.Document.published_at.desc().nullslast())
        .limit(5)
        .all()
    )

    if not articles:
        return WritingIdeasResponse(
            summary="Publish some Substack articles to get writing suggestions.",
            ideas=[],
        )

    articles_content = "\n\n---\n\n".join(
        f"Title: {article.title}\n"
        f"Content: {article.raw_text[:600]}"
        for article in articles
    )

    prompt = f"""
Analyze the author's recent articles and identify their recurring topics,
interests, writing themes, and unexplored angles.

Return:
- One short summary beginning with "You previously wrote about..."
- Exactly 3 new article title suggestions.

Rules:
- Analyze article content, not just titles.
- Suggestions must be relevant to the author's actual writing.
- Explore new angles or connections rather than repeating existing articles.
- Avoid generic ideas.
- Do not invent personal experiences or achievements.
- Keep the summary to one sentence.
- Titles should be concise and natural.
- Return JSON only, without Markdown.

Required format:
{{
  "summary": "You previously wrote about ...",
  "ideas": [
    "First article title",
    "Second article title",
    "Third article title"
  ]
}}

ARTICLES:

{articles_content}
"""

    response = generate_answer(prompt)

    try:
        data = json.loads(response)
        result = WritingIdeasResponse.model_validate(data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("AI returned an invalid writing suggestions response.") from exc

    if len(result.ideas) != 3:
        raise ValueError("AI did not return exactly three writing ideas.")

    return result
