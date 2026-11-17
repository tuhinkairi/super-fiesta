
"""Tests for root package public exports."""

import context_aware_suggestion_rag as package


def test_package_metadata():
    assert package.__version__ == "0.1.0"
    assert package.__author__

    print("Package metadata: PASS")


def test_pipeline_exports():
    assert callable(package.ContextAwareSuggestionPipeline)
    assert callable(package.ContextAwareSuggestionFacade)
    assert callable(package.PipelineStage)

    print("Pipeline exports: PASS")


def test_result_exports():
    assert package.PipelineResult is not None
    assert package.PipelineStageResult is not None
    assert package.PipelineStatus is not None

    print("Pipeline result exports: PASS")


if __name__ == "__main__":
    test_package_metadata()
    test_pipeline_exports()
    test_result_exports()

    print("\nAll package export tests passed.")
