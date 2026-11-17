from unittest.mock import Mock, patch

from modules.inspiration_ingestion.extractors.url_extractor import (
    URLExtractor,
)


def main():
    extractor = URLExtractor()

    # 1. Invalid URL scheme validation
    try:
        extractor._validate_url("ftp://example.com")
    except ValueError:
        print("Invalid scheme validation passed.")
    else:
        raise AssertionError("FTP URLs should be rejected.")

    # 2. Localhost protection
    try:
        extractor._validate_url("http://localhost")
    except ValueError:
        print("Localhost protection passed.")
    else:
        raise AssertionError("Localhost URLs should be rejected.")

    # 3. Public hostname validation
    with patch(
        "modules.inspiration_ingestion.extractors.url_extractor.socket.getaddrinfo"
    ) as mock_dns:

        mock_dns.return_value = [(2, 1, 6, "", ("93.184.216.34", 80))]

        extractor._validate_url("http://example.com")
        print("Public hostname validation passed.")

    # 4. Private IP protection
    with patch(
        "modules.inspiration_ingestion.extractors.url_extractor.socket.getaddrinfo"
    ) as mock_dns:

        mock_dns.return_value = [(2, 1, 6, "", ("192.168.1.10", 80))]

        try:
            extractor._validate_url("http://example.com")
        except ValueError:
            print("Private IP protection passed.")
        else:
            raise AssertionError("Private IP addresses should be rejected.")

    # 5. Mocked webpage extraction
    html = """
    <html>
        <head>
            <title>Creative Storytelling</title>
        </head>
        <body>
            <nav>Navigation content</nav>

            <article>
                <h1>Storytelling</h1>
                <p>Stories help people communicate ideas.</p>
            </article>

            <script>Ignore this content</script>
        </body>
    </html>
    """

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": str(len(html.encode("utf-8"))),
    }
    mock_response.encoding = "utf-8"
    mock_response.url = "https://example.com/article"

    # Simulate streamed response content.
    mock_response.iter_content = lambda chunk_size: [html.encode("utf-8")]

    # Simulate closing the HTTP response.
    mock_response.close = Mock()

    with (
        patch(
            "modules.inspiration_ingestion.extractors.url_extractor.socket.getaddrinfo",
            return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
        ),
        patch(
            "modules.inspiration_ingestion.extractors.url_extractor.requests.get",
            return_value=mock_response,
        ),
    ):

        result = extractor.extract_content("https://example.com/article")

    # 6. Verify extracted webpage content
    assert result["title"] == "Creative Storytelling"

    assert "Stories help people communicate ideas." in result["text"]

    assert "Navigation content" not in result["text"]
    assert "Ignore this content" not in result["text"]

    assert result["word_count"] > 0
    assert result["character_count"] > 0

    print("Mocked webpage extraction passed.")
    print("HTML cleanup passed.")
    print("Extracted metadata validation passed.")

    # 7. Verify response was closed.
    mock_response.close.assert_called_once()
    print("HTTP response cleanup passed.")

    print("\nAll URL extractor checks passed!")


if __name__ == "__main__":
    main()
