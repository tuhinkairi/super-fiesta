
import context_aware_suggestion_rag.utils as utils


def test_package_import():
    assert utils is not None


def test_collection_exports():
    assert callable(utils.group_by)
    assert callable(utils.partition)
    assert callable(utils.chunked)
    assert callable(utils.unique_by)


def test_converter_exports():
    assert utils.to_integer("42") == 42
    assert utils.to_float("3.14") == 3.14
    assert utils.to_boolean("true") is True


def test_formatter_exports():
    assert utils.format_bytes(1024) == "1.00 KB"
    assert utils.format_snake_case("Hello World") == "hello_world"
    assert utils.normalize_whitespace("  hello   world  ") == "hello world"


def test_validator_exports():
    assert utils.validate_non_empty_string("hello") == "hello"


def test_exception_exports():
    assert issubclass(utils.ConversionError, utils.UtilityError)
    assert issubclass(utils.CollectionError, utils.UtilityError)


def test_normalizer_exports():
    assert callable(utils.normalize_unicode)
    assert callable(utils.normalize_keyword)
    assert callable(utils.normalize_identifier)
    assert callable(utils.normalize_metadata_keys)
    assert callable(utils.normalize_url)
    assert callable(utils.normalize_text_for_search)
    assert callable(utils.normalize_tags)


def test_regex_exports():
    # Ensure regex utilities are available through the package.
    import context_aware_suggestion_rag.utils.regex_utils as regex_utils

    public_names = [
        name
        for name in dir(regex_utils)
        if not name.startswith("_")
        and (
            name.isupper()
            or (
                callable(getattr(regex_utils, name))
                and getattr(getattr(regex_utils, name), "__module__", None)
                == regex_utils.__name__
            )
        )
    ]

    for name in public_names:
        assert hasattr(utils, name), f"Missing regex export: {name}"


def test_security_utility_exports():
    assert callable(utils.generate_secure_token)
    assert callable(utils.generate_secure_password)
    assert callable(utils.sha256_hash)
    assert callable(utils.sha512_hash)
    assert callable(utils.hmac_sha256)
    assert callable(utils.constant_time_compare)
    assert callable(utils.mask_string)
    assert callable(utils.mask_email)
    assert callable(utils.redact_mapping)


def test_environment_exports():
    assert callable(utils.get_env)
    assert callable(utils.get_env_bool)
    assert callable(utils.get_env_int)
    assert callable(utils.get_env_float)
    assert callable(utils.get_env_list)
    assert callable(utils.get_env_mapping)
    assert callable(utils.get_required_env)
    assert callable(utils.set_env_defaults)
    assert callable(utils.load_env_file)


def test_all_exports_exist():
    for name in utils.__all__:
        assert hasattr(utils, name), f"Missing export: {name}"

    assert len(utils.__all__) == len(set(utils.__all__))


if __name__ == "__main__":
    tests = [
        test_package_import,
        test_collection_exports,
        test_converter_exports,
        test_formatter_exports,
        test_validator_exports,
        test_exception_exports,
        test_normalizer_exports,
        test_regex_exports,
        test_security_utility_exports,
        test_environment_exports,
        test_all_exports_exist,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All utility package tests passed.")
