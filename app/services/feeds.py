
import re
from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.core import config


class FeedError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.status_code = status_code
        super().__init__(message)


# =========================
# URL normalization
# =========================

def normalize_substack_url(url: str) -> str:
    """Normalize a Substack publication URL."""
    url = url.strip().rstrip("/")

    if not url:
        raise ValueError("Substack URL is required.")

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    return url


def normalize_medium_url(url: str) -> str:
    """Normalize a Medium profile or publication URL."""
    url = url.strip().rstrip("/")

    if not url:
        raise ValueError("Medium URL is required.")

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    url = url.replace("http://", "https://", 1)

    # Convert a feed URL back to its canonical profile URL.
    url = url.replace("medium.com/feed/", "medium.com/")

    return url


# =========================
# Feed URLs
# =========================

def get_feed_url(publication_url: str) -> str:
    """Convert Substack publication URL into its RSS feed URL."""
    publication_url = normalize_substack_url(publication_url)
    return f"{publication_url}/feed"


def get_medium_feed_url(profile_url: str) -> str:
    """Convert Medium profile URL into its RSS feed URL."""
    profile_url = normalize_medium_url(profile_url)

    if "medium.com" in profile_url:
        return f"{profile_url.replace('medium.com/', 'medium.com/feed/', 1)}"

    # Supports Medium custom domains as well.
    return f"{profile_url}/feed"


# =========================
# Content parsing
# =========================

def _html_to_text(html: str) -> str:
    """Extract readable text from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return soup.get_text(separator="\n", strip=True)


def _clean_text(text: str) -> str:
    """Normalize excessive whitespace."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _get_entry_content(entry) -> str:
    """Extract article text from RSS entry content or summary."""
    content = ""

    if entry.get("content"):
        content = "\n".join(
            item.get("value", "")
            for item in entry.content
        )

    if not content:
        content = entry.get("summary", "")

    text = _html_to_text(content)
    return _clean_text(text)


def _get_published_at(entry) -> datetime | None:
    """Convert RSS publication date to timezone-aware datetime."""
    published = entry.get("published_parsed")

    if published:
        return datetime.fromtimestamp(
            mktime(published),
            tz=timezone.utc,
        )

    updated = entry.get("updated_parsed")

    if updated:
        return datetime.fromtimestamp(
            mktime(updated),
            tz=timezone.utc,
        )

    return None


# =========================
# Generic RSS fetching
# =========================

def _fetch_feed(feed_url: str, platform: str) -> list[dict]:
    """Fetch and parse an RSS feed."""
    try:
        response = httpx.get(
            feed_url,
            timeout=config.FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 Noteway/1.0",
            },
        )
        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Failed to fetch {platform} feed: {exc}"
        ) from exc

    feed = feedparser.parse(response.text)

    if feed.bozo and not feed.entries:
        raise RuntimeError(
            f"{platform} returned an invalid RSS feed."
        )

    posts = []

    for entry in feed.entries:
        title = entry.get("title", "Untitled").strip()
        url = entry.get("link", "").strip()
        text = _get_entry_content(entry)

        if not url:
            continue

        posts.append(
            {
                "title": title,
                "url": url,
                "raw_text": text,
                "published_at": _get_published_at(entry),
            }
        )

    return posts


# =========================
# Substack
# =========================

def fetch_substack_posts(publication_url: str) -> list[dict]:
    """Fetch articles from a Substack RSS feed."""
    feed_url = get_feed_url(publication_url)
    return _fetch_feed(feed_url, "Substack")


# =========================
# Medium
# =========================

def fetch_medium_posts(profile_url: str) -> list[dict]:
    """Fetch articles from the configured Medium RSS feed."""

    if not config.MEDIUM_URL:
        raise ValueError("Medium URL is not configured.")
    
    feed_url = get_medium_feed_url(config.MEDIUM_URL)
    return _fetch_feed(feed_url, "Medium")
