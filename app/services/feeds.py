"""Fetch posts from an RSS/Atom feed and turn them into plain-text articles.

Substack uses this now; Medium (and any other feed) can reuse fetch_feed_articles
with its own URL-normalising helper."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.core import config

USER_AGENT = "Noteway/0.1 (personal knowledge assistant)"

_BLOCK_TAGS = [
    "p", "div", "li", "blockquote", "pre", "figure",
    "h1", "h2", "h3", "h4", "h5", "h6",
]


class FeedError(Exception):
    """Base class. status_code is the HTTP status the API should return."""

    status_code = 502


class InvalidFeedURL(FeedError):
    status_code = 400


class FeedFetchError(FeedError):
    status_code = 502


@dataclass
class Article:
    title: str
    url: str
    published_at: datetime | None
    text: str


def normalize_substack_feed_url(raw_url: str) -> str:
    """Accept 'name.substack.com', 'https://name.substack.com/', a post URL or a
    custom domain, and return that publication's feed URL (<origin>/feed)."""
    url = (raw_url or "").strip()
    if not url:
        raise InvalidFeedURL("Enter a Substack URL.")
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise InvalidFeedURL("Enter a valid http(s) URL.")
    return urlunparse((parsed.scheme, parsed.netloc, "/feed", "", "", ""))


def _validate_public_url(url: str) -> None:
    """Refuse URLs that point at this machine or a private network, so the sync
    endpoint can't be used to poke at internal services."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise InvalidFeedURL("Enter a valid http(s) URL.")
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise InvalidFeedURL("Could not resolve that host.") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            raise InvalidFeedURL("That address is not allowed.")


def html_to_text(html: str) -> str:
    """Strip HTML to readable plain text, keeping paragraph breaks."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for block in soup.find_all(_BLOCK_TAGS):
        block.append("\n\n")
    text = soup.get_text()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _published_at(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


def fetch_feed_articles(feed_url: str) -> list[Article]:
    """Download a feed and return its entries as plain-text articles.

    Free Substack posts carry their full body in the feed; paid posts only carry
    a teaser, and that is all we store. Feeds list recent posts only, so older
    archive posts are not included."""
    _validate_public_url(feed_url)
    try:
        response = httpx.get(
            feed_url,
            timeout=config.FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise FeedFetchError(
            f"The site returned an error ({exc.response.status_code}) for that feed."
        ) from exc
    except httpx.HTTPError as exc:
        raise FeedFetchError("Could not reach that feed. Check the URL and try again.") from exc

    parsed = feedparser.parse(response.content)
    # feedparser leaves `version` empty when the content isn't a feed at all
    # (e.g. an HTML page). A real feed with zero posts has a version and is fine.
    if not parsed.entries and not parsed.version:
        raise FeedFetchError("That URL did not return a valid RSS feed.")

    articles: list[Article] = []
    for entry in parsed.entries:
        url = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not url or not title:
            continue
        content = entry.get("content") or []
        html = content[0].get("value", "") if content else entry.get("summary", "")
        articles.append(
            Article(
                title=title,
                url=url,
                published_at=_published_at(entry),
                text=html_to_text(html),
            )
        )
    return articles