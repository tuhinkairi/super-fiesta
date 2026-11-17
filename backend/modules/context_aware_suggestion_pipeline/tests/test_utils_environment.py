
import os
import tempfile
from pathlib import Path

from context_aware_suggestion_rag.utils.environment import (
    get_env,
    get_env_bool,
    get_env_float,
    get_env_int,
    get_env_list,
    get_env_mapping,
    get_required_env,
    load_env_file,
    set_env_defaults,
)


def test_get_env():
    os.environ["TEST_CASR_VALUE"] = " hello "
    assert get_env("TEST_CASR_VALUE") == "hello"
    assert get_env("TEST_CASR_VALUE", strip=False) == " hello "
    assert get_env("TEST_CASR_MISSING", "fallback") == "fallback"


def test_get_env_bool():
    os.environ["TEST_CASR_BOOL"] = "true"
    assert get_env_bool("TEST_CASR_BOOL") is True

    os.environ["TEST_CASR_BOOL"] = "off"
    assert get_env_bool("TEST_CASR_BOOL") is False

    assert get_env_bool("TEST_CASR_MISSING_BOOL", True) is True


def test_get_env_int():
    os.environ["TEST_CASR_INT"] = "42"
    assert get_env_int("TEST_CASR_INT") == 42
    assert get_env_int("TEST_CASR_MISSING_INT", 10) == 10


def test_get_env_float():
    os.environ["TEST_CASR_FLOAT"] = "3.14"
    assert get_env_float("TEST_CASR_FLOAT") == 3.14
    assert get_env_float("TEST_CASR_MISSING_FLOAT", 1.5) == 1.5


def test_get_required_env():
    os.environ["TEST_CASR_REQUIRED"] = "configured"
    assert get_required_env("TEST_CASR_REQUIRED") == "configured"


def test_get_env_list():
    os.environ["TEST_CASR_LIST"] = "AI, ML, RAG"
    assert get_env_list("TEST_CASR_LIST") == ["AI", "ML", "RAG"]


def test_get_env_mapping():
    result = get_env_mapping(
        "CASR_TEST_",
        environ={
            "CASR_TEST_NAME": "pipeline",
            "CASR_TEST_MODE": "development",
            "OTHER_VALUE": "ignored",
        },
    )

    assert result == {
        "NAME": "pipeline",
        "MODE": "development",
    }


def test_set_env_defaults():
    set_env_defaults({
        "TEST_CASR_DEFAULT": "first",
    })
    assert os.environ["TEST_CASR_DEFAULT"] == "first"

    set_env_defaults({
        "TEST_CASR_DEFAULT": "second",
    })
    assert os.environ["TEST_CASR_DEFAULT"] == "first"


def test_load_env_file():
    with tempfile.TemporaryDirectory() as directory:
        env_path = Path(directory) / ".env.test"

        env_path.write_text(
            "TEST_CASR_FILE_ONE=hello\n"
            "TEST_CASR_FILE_TWO=\"world\"\n"
            "# comment\n"
            "export TEST_CASR_FILE_THREE=rag\n",
            encoding="utf-8",
        )

        loaded = load_env_file(env_path, overwrite=True)

        assert loaded == 3
        assert os.environ["TEST_CASR_FILE_ONE"] == "hello"
        assert os.environ["TEST_CASR_FILE_TWO"] == "world"
        assert os.environ["TEST_CASR_FILE_THREE"] == "rag"


if __name__ == "__main__":
    tests = [
        test_get_env,
        test_get_env_bool,
        test_get_env_int,
        test_get_env_float,
        test_get_required_env,
        test_get_env_list,
        test_get_env_mapping,
        test_set_env_defaults,
        test_load_env_file,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All environment utility tests passed.")
