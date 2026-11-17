"""
RSS-based news intelligence provider.

Collects news articles from configured RSS feeds and normalizes
them into the package's NewsData model.
"""

import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import feedparser
import httpx

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.trend_config import (
    get_trend_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.base import BaseNewsProvider
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import NewsData

logger = get_logger(__name__)


class RSSNewsProvider(BaseNewsProvider):
    """Collect news articles from configured RSS feeds."""

    def __init__(
        self,
        *,
        timeout: float = 15.0,
        max_age_hours: int | None = None,
        user_agent: str | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        if max_age_hours is not None and max_age_hours < 1:
            raise ValueError("max_age_hours must be positive")

        self.settings = get_trend_config()
        self.timeout = timeout

        self.max_age_hours = (
            max_age_hours
            if max_age_hours is not None
            else self.settings.news_lookback_hours
        )

        self.user_agent = (
            user_agent
            or self.settings.news_user_agent
        )

        self._client: httpx.Client | None = None
        self._connected = False

    def connect(self) -> None:
        """Initialize the HTTP client."""
        if self._connected and self._client is not None:
            return

        try:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
            )

            self._connected = True
            logger.info("RSS news provider connected")

        except Exception:
            self._client = None
            self._connected = False
            raise

    def _get_client(self) -> httpx.Client:
        """Return an initialized HTTP client."""
        if not self._connected or self._client is None:
            self.connect()

        if self._client is None:
            raise RuntimeError("HTTP client initialization failed")

        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()

        self._client = None
        self._connected = False

    def health_check(self) -> bool:
        """Check whether at least one configured feed is reachable."""
        if not self.settings.news_enabled:
            return False

        for feed_url in self.settings.news_rss_feeds:
            try:
                response = self._get_client().get(str(feed_url))
                response.raise_for_status()
                return True

            except Exception as exc:
                logger.warning(
                    "RSS health check failed for %s: %s",
                    feed_url,
                    exc,
                )

        return False

    @staticmethod
    def _parse_datetime(entry: Any) -> datetime | None:
        """Parse an RSS article publication date."""
        parsed = (
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )

        if parsed is not None:
            try:
                from calendar import timegm

                return datetime.fromtimestamp(
                    timegm(parsed),
                    tz=timezone.utc,
                )
            except (TypeError, ValueError, OverflowError):
                pass

        date_text = (
            getattr(entry, "published", None)
            or getattr(entry, "updated", None)
        )

        if not date_text:
            return None

        try:
            parsed_date = parsedate_to_datetime(date_text)

            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

            return parsed_date.astimezone(timezone.utc)

        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _extract_text(entry: Any, field: str) -> str:
        """Extract and clean text from an RSS entry."""
        value = getattr(entry, field, "")

        if isinstance(value, list) and value:
            value = value[0].get("value", "")

        text = re.sub(r"<[^>]+>", " ", str(value))
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _extract_source(entry: Any, feed_url: str) -> str:
        """Extract the article source name."""
        source = getattr(entry, "source", None)

        if source:
            source_title = source.get("title")
            if source_title:
                return str(source_title).strip()

        hostname = urlparse(feed_url).hostname

        if hostname:
            return hostname.removeprefix("www.")

        return "unknown"

    @staticmethod
    def _extract_keywords(title: str, description: str) -> list[str]:
        """Extract simple candidate keywords from article text."""
        stop_words = {
            "the", "and", "for", "with", "from", "this",
            "that", "are", "was", "were", "will", "has",
            "have", "had", "into", "about", "after", "before",
            "their", "there", "they", "them", "you", "your",
            "its", "his", "her", "our", "but", "not", "can",
        }

        words = re.findall(
            r"\b[A-Za-z][A-Za-z0-9+#.-]{2,}\b",
            f"{title} {description}",
        )

        keywords: list[str] = []
        seen: set[str] = set()

        for word in words:
            normalized = word.casefold()

            if normalized in stop_words or normalized in seen:
                continue

            seen.add(normalized)
            keywords.append(word)

            if len(keywords) >= 15:
                break

        return keywords

    def fetch_news(
        self,
        *,
        query: str | None = None,
        region: str = "IN",
        language: str = "en",
        limit: int = 30,
    ) -> list[NewsData]:
        """Fetch and normalize news articles from configured RSS feeds."""
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("limit must be a positive integer")

        if not region.strip():
            raise ValueError("region cannot be empty")

        if not language.strip():
            raise ValueError("language cannot be empty")

        if query is not None and not query.strip():
            raise ValueError("query cannot be empty when provided")

        if not self.settings.news_enabled:
            logger.info("News collection is disabled")
            return []

        feeds = self.settings.news_rss_feeds

        if not feeds:
            logger.warning("No RSS feeds are configured")
            return []

        client = self._get_client()

        cutoff = datetime.now(timezone.utc) - timedelta(
            hours=self.max_age_hours
        )

        articles: list[NewsData] = []
        seen_urls: set[str] = set()
        query_terms = (
            query.casefold().split()
            if query is not None
            else []
        )

        for feed_url in feeds:
            try:
                response = client.get(str(feed_url))
                response.raise_for_status()

                parsed_feed = feedparser.parse(response.content)

                if parsed_feed.bozo and not parsed_feed.entries:
                    logger.warning(
                        "Could not parse RSS feed: %s",
                        feed_url,
                    )
                    continue

                for entry in parsed_feed.entries:
                    title = self._extract_text(entry, "title")
                    description = self._extract_text(entry, "summary")

                    article_url = str(
                        getattr(entry, "link", "")
                    ).strip()

                    if not title or not article_url:
                        continue

                    if article_url in seen_urls:
                        continue

                    published_at = self._parse_datetime(entry)

                    if published_at is not None and published_at < cutoff:
                        continue

                    combined_text = (
                        f"{title} {description}".casefold()
                    )

                    if query_terms and not all(
                        term in combined_text for term in query_terms
                    ):
                        continue

                    try:
                        article = NewsData(
                            title=title,
                            description=description,
                            url=article_url,
                            source_name=self._extract_source(
                                entry,
                                str(feed_url),
                            ),
                            published_at=published_at,
                            language=language,
                            region=region,
                            keywords=self._extract_keywords(
                                title,
                                description,
                            ),
                            metadata={
                                "feed_url": str(feed_url),
                                "feed_language": language,
                                "feed_region": region,
                            },
                        )

                    except Exception as exc:
                        logger.warning(
                            "Skipping invalid RSS article '%s': %s",
                            title,
                            exc,
                        )
                        continue

                    seen_urls.add(article_url)
                    articles.append(article)

                    if len(articles) >= limit:
                        return articles

            except Exception as exc:
                logger.warning(
                    "Failed to process RSS feed %s: %s",
                    feed_url,
                    exc,
                )

        return articles
