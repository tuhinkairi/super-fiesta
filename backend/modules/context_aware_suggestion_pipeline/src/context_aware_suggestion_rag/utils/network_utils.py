"""Reusable network and HTTP utilities."""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Mapping
from typing import Any
from urllib.parse import (
    parse_qs,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)

import httpx

from .validators import validate_non_empty_string, validate_url


def parse_url(url: str) -> dict[str, Any]:
    """Parse an absolute HTTP or HTTPS URL."""
    validated_url = validate_url(url)
    parsed = urlparse(validated_url)

    return {
        "scheme": parsed.scheme.lower(),
        "hostname": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path,
        "query": parsed.query,
        "fragment": parsed.fragment,
        "username": parsed.username,
        "password": parsed.password,
    }


def build_url(
    base_url: str,
    path: str = "",
    query_params: Mapping[str, Any] | None = None,
) -> str:
    """Build a URL from a base URL, path, and query parameters."""
    base_url = validate_url(base_url)
    parsed = urlparse(base_url)

    if not isinstance(path, str):
        raise TypeError("path must be a string.")

    if query_params is not None and not isinstance(query_params, Mapping):
        raise TypeError("query_params must be a mapping or None.")

    result = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

    if query_params:
        parsed_result = urlparse(result)
        existing = parse_qs(parsed_result.query, keep_blank_values=True)

        for key, value in query_params.items():
            key = validate_non_empty_string(key, "query parameter name")

            if isinstance(value, (list, tuple)):
                existing[key] = [str(item) for item in value]
            elif value is None:
                existing[key] = [""]
            else:
                existing[key] = [str(value)]

        result = urlunparse(
            parsed_result._replace(
                query=urlencode(existing, doseq=True)
            )
        )

    return result


def add_query_params(
    url: str,
    params: Mapping[str, Any],
) -> str:
    """Add or replace query parameters in a URL."""
    return build_url(url, query_params=params)


def get_query_params(url: str) -> dict[str, list[str]]:
    """Extract query parameters from a URL."""
    validated_url = validate_url(url)
    return parse_qs(
        urlparse(validated_url).query,
        keep_blank_values=True,
    )


def normalize_url(
    url: str,
    *,
    remove_fragment: bool = True,
    remove_trailing_slash: bool = False,
) -> str:
    """Normalize URL scheme, hostname, and optional components."""
    validated_url = validate_url(url)
    parsed = urlparse(validated_url)

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower() if parsed.hostname else ""

    if not hostname:
        raise ValueError("URL must contain a hostname.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not supported.")

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("URL contains an invalid port.") from exc

    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"

    default_port = (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    )

    netloc = hostname

    if port is not None and not default_port:
        netloc = f"{netloc}:{port}"

    path = parsed.path or "/"

    if remove_trailing_slash and path != "/":
        path = path.rstrip("/")

    return urlunparse(
        (
            scheme,
            netloc,
            path,
            parsed.params,
            parsed.query,
            "" if remove_fragment else parsed.fragment,
        )
    )


def validate_http_status(
    status_code: int,
    *,
    accepted_codes: set[int] | None = None,
) -> bool:
    """Validate an HTTP response status code."""
    if isinstance(status_code, bool) or not isinstance(status_code, int):
        raise TypeError("status_code must be an integer.")

    if not 100 <= status_code <= 599:
        raise ValueError("status_code must be between 100 and 599.")

    if accepted_codes is not None:
        if not isinstance(accepted_codes, set):
            raise TypeError("accepted_codes must be a set or None.")

        if any(
            isinstance(code, bool)
            or not isinstance(code, int)
            or not 100 <= code <= 599
            for code in accepted_codes
        ):
            raise ValueError("accepted_codes contains an invalid status code.")

        return status_code in accepted_codes

    return 200 <= status_code < 300


def validate_json_response(response: httpx.Response) -> Any:
    """Validate and deserialize a JSON HTTP response."""
    if not isinstance(response, httpx.Response):
        raise TypeError("response must be an httpx.Response.")

    if not 200 <= response.status_code < 300:
        raise httpx.HTTPStatusError(
            f"Unexpected HTTP status: {response.status_code}",
            request=response.request,
            response=response,
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError("HTTP response does not contain valid JSON.") from exc


def get_response_header(
    response: httpx.Response,
    header_name: str,
    default: str | None = None,
) -> str | None:
    """Get a response header without raising KeyError."""
    if not isinstance(response, httpx.Response):
        raise TypeError("response must be an httpx.Response.")

    header_name = validate_non_empty_string(header_name, "header_name")

    return response.headers.get(header_name, default)


def is_host_resolvable(hostname: str, port: int = 443) -> bool:
    """Check whether a hostname can be resolved through DNS."""
    hostname = validate_non_empty_string(hostname, "hostname")

    if isinstance(port, bool) or not isinstance(port, int):
        raise TypeError("port must be an integer.")

    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535.")

    try:
        socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        return True
    except socket.gaierror:
        return False


def is_public_ip_address(address: str) -> bool:
    """Check whether an IP address is globally routable."""
    address = validate_non_empty_string(address, "address")

    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False

    return parsed.is_global


def create_http_client(
    *,
    timeout: float = 10.0,
    follow_redirects: bool = True,
    headers: Mapping[str, str] | None = None,
) -> httpx.Client:
    """Create a configured synchronous HTTP client."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be numeric.")

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero.")

    if not isinstance(follow_redirects, bool):
        raise TypeError("follow_redirects must be a boolean.")

    if headers is not None and not isinstance(headers, Mapping):
        raise TypeError("headers must be a mapping or None.")

    return httpx.Client(
        timeout=float(timeout),
        follow_redirects=follow_redirects,
        headers=dict(headers) if headers is not None else None,
    )


def create_async_http_client(
    *,
    timeout: float = 10.0,
    follow_redirects: bool = True,
    headers: Mapping[str, str] | None = None,
) -> httpx.AsyncClient:
    """Create a configured asynchronous HTTP client."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be numeric.")

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero.")

    if not isinstance(follow_redirects, bool):
        raise TypeError("follow_redirects must be a boolean.")

    if headers is not None and not isinstance(headers, Mapping):
        raise TypeError("headers must be a mapping or None.")

    return httpx.AsyncClient(
        timeout=float(timeout),
        follow_redirects=follow_redirects,
        headers=dict(headers) if headers is not None else None,
    )
