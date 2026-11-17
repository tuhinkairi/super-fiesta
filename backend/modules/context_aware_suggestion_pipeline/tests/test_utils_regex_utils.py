
from context_aware_suggestion_rag.utils.regex_utils import (
    compile_pattern,
    contains_pattern,
    extract_emails,
    extract_hashtags,
    extract_mentions,
    extract_urls,
    extract_words,
    find_all,
    remove_matches,
    replace_pattern,
    split_by_pattern,
)


def test_compile_pattern():
    pattern = compile_pattern(r"\d+")
    assert pattern.findall("A12 B34") == ["12", "34"]


def test_extract_urls():
    result = extract_urls(
        "Visit https://example.com and http://example.org"
    )
    assert result == [
        "https://example.com",
        "http://example.org",
    ]


def test_extract_emails():
    result = extract_emails(
        "Contact a@example.com or b@test.org"
    )
    assert result == ["a@example.com", "b@test.org"]


def test_extract_hashtags():
    assert extract_hashtags("#AI #MachineLearning") == [
        "#AI",
        "#MachineLearning",
    ]


def test_extract_mentions():
    assert extract_mentions("@alice hello @bob") == [
        "@alice",
        "@bob",
    ]


def test_extract_words():
    result = extract_words("AI-powered systems aren't magic")
    assert result == [
        "AI-powered",
        "systems",
        "aren't",
        "magic",
    ]


def test_find_all():
    assert find_all(r"\d+", "A12 B34") == ["12", "34"]


def test_contains_pattern():
    assert contains_pattern(r"\d+", "version 3") is True
    assert contains_pattern(r"\d+", "no numbers") is False


def test_replace_pattern():
    assert replace_pattern(r"\d+", "[NUMBER]", "AI 2026") == (
        "AI [NUMBER]"
    )


def test_split_by_pattern():
    assert split_by_pattern(r"[,;]", "AI,ML;RAG") == [
        "AI",
        "ML",
        "RAG",
    ]


def test_remove_matches():
    assert remove_matches(r"\d+", "AI2026RAG") == "AIRAG"


if __name__ == "__main__":
    tests = [
        test_compile_pattern,
        test_extract_urls,
        test_extract_emails,
        test_extract_hashtags,
        test_extract_mentions,
        test_extract_words,
        test_find_all,
        test_contains_pattern,
        test_replace_pattern,
        test_split_by_pattern,
        test_remove_matches,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All regex utility tests passed.")
