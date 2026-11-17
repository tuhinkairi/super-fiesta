
from context_aware_suggestion_rag.interfaces.recommendation_provider import (
    RecommendationProvider,
)
from context_aware_suggestion_rag.recommendation.models import (
    Recommendation,
)


class FakeRecommendationProvider(RecommendationProvider):

    def generate(self, candidates):
        return []

    def health_check(self):
        return True


def main():
    provider = FakeRecommendationProvider()

    assert isinstance(provider, RecommendationProvider)
    print("Recommendation provider inheritance: PASS")

    assert provider.health_check()
    print("Recommendation provider health check: PASS")

    recommendations = provider.generate([])
    assert recommendations == []
    print("Recommendation generation interface: PASS")

    provider.configure({"minimum_score": 0.5})
    print("Provider configuration interface: PASS")

    provider.close()
    print("Provider close interface: PASS")

    print("\nAll recommendation provider interface tests passed.")


if __name__ == "__main__":
    main()
