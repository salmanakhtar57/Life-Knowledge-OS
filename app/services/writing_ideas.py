
import json

from sqlalchemy.orm import Session

from app.models import models
from app.schemas.schemas import WritingIdeasResponse
from app.services.generation import generate_answer


def _get_writing_ideas(
    db: Session,
    platform: models.SourcePlatform,
) -> WritingIdeasResponse:
    cached = (
        db.query(models.WritingSuggestion)
        .filter(models.WritingSuggestion.platform == platform.value)
        .first()
    )

    if cached:
        return WritingIdeasResponse(
            summary=cached.summary,
            ideas=cached.ideas,
        )

    return _refresh_writing_ideas(db, platform)


def _refresh_writing_ideas(
    db: Session,
    platform: models.SourcePlatform,
) -> WritingIdeasResponse:
    is_medium = platform == models.SourcePlatform.MEDIUM
    platform_name = "Medium" if is_medium else "Substack"
    article_limit = 3 if is_medium else 5

    articles = (
        db.query(models.Document)
        .join(models.Source)
        .filter(models.Source.platform == platform)
        .order_by(models.Document.published_at.desc().nullslast())
        .limit(article_limit)
        .all()
    )

    if not articles:
        result = WritingIdeasResponse(
            summary=f"Publish some {platform_name} articles to get writing suggestions.",
            ideas=[],
        )
    else:
        articles_content = "\n\n---\n\n".join(
            f"Title: {article.title}\n"
            f"Content: {article.raw_text[:600]}"
            for article in articles
        )

        prompt = f"""
Analyze the author's recent articles to understand their writing style,
interests, experiences, opinions, and recurring topics.

Return:
- One short summary of the author's previous writing.
- Exactly 3 new article title suggestions.

Summary rules:
- Use simple, everyday English.
- Keep it very short, ideally no more than 15-20 words.
- It should fit within approximately 1-1.5 lines on a dashboard.
- Begin with "You previously wrote about..."
- Avoid unnecessary details or complicated wording.

Suggestion rules:
- Suggest realistic, specific article ideas the author could genuinely write.
- Make ideas closely related to the author's actual interests, experiences,
  previous articles, or ongoing learning.
- Prefer narrow, focused topics over broad subjects.
- Suggest practical angles, personal observations, lessons, problems,
  decisions, or experiences that could form an actual article.
- Explore new angles within the author's existing interests rather than
  repeating topics they have already covered.
- Avoid generic, motivational, philosophical, or overly abstract topics.
- Avoid ideas that sound like generic AI-generated blog titles.
- Do not invent personal experiences, opinions, or achievements.
- Titles should sound natural, simple, and human.
- Each suggestion should be specific enough that the author immediately
  knows what they could write about.

Return JSON only, without Markdown.

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
            raise ValueError(
                "AI returned an invalid writing suggestions response."
            ) from exc

        if len(result.ideas) != 3:
            raise ValueError(
                "AI did not return exactly three writing ideas."
            )

    cached = (
        db.query(models.WritingSuggestion)
        .filter(models.WritingSuggestion.platform == platform.value)
        .first()
    )

    if cached:
        cached.summary = result.summary
        cached.ideas = result.ideas
    else:
        cached = models.WritingSuggestion(
            platform=platform.value,
            summary=result.summary,
            ideas=result.ideas,
        )
        db.add(cached)

    db.commit()
    db.refresh(cached)

    return result


# Substack
def get_substack_writing_ideas(db: Session) -> WritingIdeasResponse:
    return _get_writing_ideas(db, models.SourcePlatform.SUBSTACK)


def refresh_substack_writing_ideas(db: Session) -> WritingIdeasResponse:
    return _refresh_writing_ideas(db, models.SourcePlatform.SUBSTACK)


# Medium
def get_medium_writing_ideas(db: Session) -> WritingIdeasResponse:
    return _get_writing_ideas(db, models.SourcePlatform.MEDIUM)


def refresh_medium_writing_ideas(db: Session) -> WritingIdeasResponse:
    return _refresh_writing_ideas(db, models.SourcePlatform.MEDIUM)


