
import httpx

from context_aware_suggestion_rag.utils.network_utils import (
    add_query_params,
    build_url,
    create_async_http_client,
    create_http_client,
    get_query_params,
    get_response_header,
    is_host_resolvable,
    is_public_ip_address,
    normalize_url,
    parse_url,
    validate_http_status,
    validate_json_response,
)


def test_parse_url():
    result = parse_url("https://example.com/api/data?page=2")

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/api/data"
    assert result["query"] == "page=2"


def test_build_url():
    result = build_url(
        "https://example.com",
        "/api/search",
        {"q": "machine learning", "page": 2},
    )

    assert result.startswith("https://example.com/api/search?")
    assert "page=2" in result


def test_query_parameters():
    url = add_query_params(
        "https://example.com/search",
        {"q": "AI", "page": 1},
    )

    params = get_query_params(url)

    assert params["q"] == ["AI"]
    assert params["page"] == ["1"]


def test_normalize_url():
    result = normalize_url(
        "HTTPS://Example.COM:443/docs/#section",
    )

    assert result == "https://example.com/docs/"


def test_http_status_validation():
    assert validate_http_status(200) is True
    assert validate_http_status(404) is False
    assert validate_http_status(404, accepted_codes={404}) is True


def test_json_response_validation():
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        200,
        request=request,
        json={"status": "ok"},
    )

    assert validate_json_response(response) == {"status": "ok"}


def test_response_headers():
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(
        200,
        request=request,
        headers={"Content-Type": "application/json"},
    )

    assert get_response_header(response, "Content-Type") == "application/json"
    assert get_response_header(response, "X-Missing") is None


def test_ip_validation():
    assert is_public_ip_address("8.8.8.8") is True
    assert is_public_ip_address("127.0.0.1") is False
    assert is_public_ip_address("not-an-ip") is False


def test_http_client_creation():
    client = create_http_client(timeout=5)

    try:
        assert isinstance(client, httpx.Client)
    finally:
        client.close()


def test_async_http_client_creation():
    client = create_async_http_client(timeout=5)

    assert isinstance(client, httpx.AsyncClient)


if __name__ == "__main__":
    tests = [
        test_parse_url,
        test_build_url,
        test_query_parameters,
        test_normalize_url,
        test_http_status_validation,
        test_json_response_validation,
        test_response_headers,
        test_ip_validation,
        test_http_client_creation,
        test_async_http_client_creation,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All network utility tests passed.")
