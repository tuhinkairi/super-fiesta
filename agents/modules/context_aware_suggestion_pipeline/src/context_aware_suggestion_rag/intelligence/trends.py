"""
Google Trends intelligence provider.

Uses PyTrends to collect trending searches and related queries.
The provider is isolated behind BaseTrendProvider so it can
be replaced without changing the application pipeline.
"""

from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.retry import retry_operation
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import TrendCollectionError
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.base import BaseTrendProvider
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import TrendData

logger = get_logger(__name__)



class GoogleTrendsProvider(BaseTrendProvider):
    """Collect trend information through the PyTrends library."""

    def __init__(
        self,
        *,
        timeout: tuple[int, int] = (10, 25),
        retries: int = 2,
    ) -> None:
        if not isinstance(timeout, tuple) or len(timeout) != 2:
            raise ValueError("timeout must be a tuple of (connect, read) seconds")

        if any(
            not isinstance(value, int) or value <= 0
            for value in timeout
        ):
            raise ValueError("timeout values must be positive integers")

        if not isinstance(retries, int) or retries < 1:
            raise ValueError("retries must be a positive integer")

        self.timeout = timeout
        self.retries = retries
        self._client: Any = None
        self._connected = False

    def connect(self) -> None:
        """Initialize the PyTrends client."""
        if self._connected:
            return

        try:
            from pytrends.request import TrendReq

            self._client = TrendReq(
                hl="en-US",
                tz=330,
                timeout=self.timeout,
                retries=self.retries,
                backoff_factor=0.5,
            )

            self._connected = True

            logger.info("Google Trends provider connected")

        except Exception as exc:
            self._client = None
            self._connected = False

            raise TrendCollectionError(
                f"Could not connect to Google Trends: {exc}"
            ) from exc

    def _get_client(self) -> Any:
        """Return an initialized PyTrends client."""
        if not self._connected or self._client is None:
            self.connect()

        return self._client

    @retry_operation(attempts=2)
    def health_check(self) -> bool:
        """Check whether Google Trends is reachable."""
        try:
            client = self._get_client()
            client.trending_searches(pn="india")
            return True

        except Exception as exc:
            logger.warning("Google Trends health check failed: %s", exc)
            return False

    def fetch_trends(
        self,
        *,
        region: str = "IN",
        language: str = "en",
        timeframe: str = "now 7-d",
        limit: int = 20,
    ) -> list[TrendData]:
        """Fetch trending searches for the requested region."""
        if not isinstance(region, str) or not region.strip():
            raise ValueError("region cannot be empty")

        if not isinstance(language, str) or not language.strip():
            raise ValueError("language cannot be empty")

        if not isinstance(timeframe, str) or not timeframe.strip():
            raise ValueError("timeframe cannot be empty")

        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")

        try:
            client = self._get_client()
            client.hl = f"{language}-{region}"

            data = client.trending_searches(pn=region.lower())

            if data is None or data.empty:
                return []

            trends: list[TrendData] = []

            for keyword in data.iloc[:, 0].dropna().head(limit):
                keyword_text = str(keyword).strip()

                if not keyword_text:
                    continue

                trends.append(
                    TrendData(
                        keyword=keyword_text,
                        value=0.0,
                        region=region,
                        language=language,
                        source="google_trends",
                        metadata={
                            "timeframe": timeframe,
                            "data_type": "trending_search",
                        },
                    )
                )

            return trends

        except TrendCollectionError:
            raise

        except Exception as exc:
            logger.exception("Failed to fetch Google Trends data")

            raise TrendCollectionError(
                f"Google Trends collection failed: {exc}"
            ) from exc

    def fetch_related_queries(
        self,
        keyword: str,
        *,
        region: str = "IN",
        limit: int = 10,
    ) -> list[str]:
        """Fetch related queries for a search keyword."""
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("keyword cannot be empty")

        if not isinstance(region, str) or not region.strip():
            raise ValueError("region cannot be empty")

        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")

        try:
            client = self._get_client()

            client.build_payload(
                [keyword.strip()],
                timeframe="now 7-d",
                geo=region,
            )

            response = client.related_queries()

            if not response:
                return []

            keyword_data = response.get(keyword.strip(), {})
            top_queries = keyword_data.get("top")

            if top_queries is None or top_queries.empty:
                return []

            return [
                str(query).strip()
                for query in top_queries["query"].dropna().head(limit)
                if str(query).strip()
            ]

        except Exception as exc:
            logger.exception(
                "Failed to fetch related queries for keyword: %s",
                keyword,
            )

            raise TrendCollectionError(
                f"Related query collection failed: {exc}"
            ) from exc
