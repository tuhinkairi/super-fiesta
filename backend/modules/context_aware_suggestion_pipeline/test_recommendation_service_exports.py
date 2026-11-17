
from context_aware_suggestion_rag.recommendation import (
    RecommendationService,
    create_recommendation_service,
    RecommendationConfig,
    get_recommendation_config,
)

service = RecommendationService()
factory_service = create_recommendation_service()
config = get_recommendation_config()

assert isinstance(service, RecommendationService)
assert isinstance(factory_service, RecommendationService)
assert isinstance(config, RecommendationConfig)

print("Recommendation service import: PASS")
print("Recommendation service factory export: PASS")
print("Recommendation configuration import: PASS")
print("All recommendation service exports passed.")
