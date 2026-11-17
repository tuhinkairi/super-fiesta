
from context_aware_suggestion_rag.interfaces.intelligence_provider import (
    IntelligenceProvider,
    TrendProvider,
    NewsProvider,
)
from context_aware_suggestion_rag.intelligence.models import (
    TrendData,
    NewsData,
)


class FakeTrendProvider(IntelligenceProvider, TrendProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def fetch_trends(
        self,
        keywords=None,
        region="IN",
        timeframe="now 7-d",
        category=0,
        limit=20,
    ):
        return [
            TrendData(keyword="AI", value=85.0)
        ]

    def fetch_related_queries(self, keyword):
        return {"top": [], "rising": []}


class FakeNewsProvider(IntelligenceProvider, NewsProvider):

    def connect(self):
        pass

    def health_check(self):
        return True

    def fetch_news(self, query=None, limit=30, lookback_hours=72):
        return []


def main():
    trends = FakeTrendProvider()
    news = FakeNewsProvider()

    assert isinstance(trends, IntelligenceProvider)
    assert isinstance(trends, TrendProvider)
    assert isinstance(news, IntelligenceProvider)
    assert isinstance(news, NewsProvider)
    print("Provider inheritance: PASS")

    assert trends.health_check()
    assert news.health_check()
    print("Provider health checks: PASS")

    trend_results = trends.fetch_trends(keywords=["AI"])

    assert len(trend_results) == 1
    assert isinstance(trend_results[0], TrendData)
    print("Trend collection interface: PASS")

    related = trends.fetch_related_queries("AI")
    assert isinstance(related, dict)
    print("Related query interface: PASS")

    news_results = news.fetch_news(query="AI")

    assert isinstance(news_results, list)
    assert all(isinstance(item, NewsData) for item in news_results)
    print("News collection interface: PASS")

    trends.close()
    news.close()
    print("Provider close interface: PASS")

    print("\nAll intelligence provider interface tests passed.")


if __name__ == "__main__":
    main()
