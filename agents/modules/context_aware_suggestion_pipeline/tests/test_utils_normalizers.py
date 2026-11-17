
from context_aware_suggestion_rag.utils.normalizers import (
    normalize_identifier,
    normalize_keyword,
    normalize_metadata_keys,
    normalize_tags,
    normalize_text_for_search,
    normalize_unicode,
    normalize_url,
    normalize_whitespace,
)


def test_normalize_unicode():
    assert normalize_unicode("café") == "café"


def test_normalize_whitespace():
    assert normalize_whitespace("  hello   world \n") == "hello world"


def test_normalize_keyword():
    assert normalize_keyword("  Machine LEARNING  ") == "machine learning"


def test_normalize_identifier():
    assert normalize_identifier("Context Aware-RAG") == "context_aware_rag"


def test_normalize_metadata_keys():
    result = normalize_metadata_keys({
        " Document Name ": "report.pdf",
        "SOURCE TYPE": "document",
    })

    assert result == {
        "document name": "report.pdf",
        "source type": "document",
    }


def test_normalize_url():
    result = normalize_url("HTTPS://Example.COM:443/article#section")

    assert result == "https://example.com/article"


def test_normalize_url_preserve_fragment():
    result = normalize_url(
        "https://example.com/article#section",
        remove_fragment=False,
    )

    assert result == "https://example.com/article#section"


def test_normalize_text_for_search():
    assert normalize_text_for_search(
        "  Context   AWARE RAG "
    ) == "context aware rag"


def test_normalize_tags():
    result = normalize_tags([
        "AI",
        "Machine Learning",
        "ai",
        "RAG",
        "",
    ])

    assert result == ["ai", "machine learning", "rag"]


if __name__ == "__main__":
    tests = [
        test_normalize_unicode,
        test_normalize_whitespace,
        test_normalize_keyword,
        test_normalize_identifier,
        test_normalize_metadata_keys,
        test_normalize_url,
        test_normalize_url_preserve_fragment,
        test_normalize_text_for_search,
        test_normalize_tags,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All normalizer utility tests passed.")
