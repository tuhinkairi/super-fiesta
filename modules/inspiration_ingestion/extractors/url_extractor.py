
import ipaddress
import socket

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class URLExtractor:
    MAX_RESPONSE_BYTES = 5 * 1024 * 1024
    MAX_REDIRECTS = 5
    REDIRECT_CODES = {301, 302, 303, 307, 308}

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def _validate_url(self, url: str):
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        parsed = urlparse(url.strip())

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are supported.")

        if not parsed.hostname:
            raise ValueError("Invalid URL.")

        if parsed.username or parsed.password:
            raise ValueError("URL credentials are not allowed.")

        try:
            port = parsed.port
        except ValueError as error:
            raise ValueError("Invalid URL port.") from error

        hostname = parsed.hostname

        if hostname.lower() == "localhost" or hostname.lower().endswith(".local"):
            raise ValueError("Local network URLs are not allowed.")

        try:
            addresses = socket.getaddrinfo(
                hostname,
                port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as error:
            raise ValueError("Unable to resolve URL hostname.") from error

        if not addresses:
            raise ValueError("No valid IP address found.")

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ValueError(
                    "Private or non-public IP addresses are not allowed."
                )

    def _download_page(self, url: str) -> tuple[str, str]:
        current_url = url

        for redirect_count in range(self.MAX_REDIRECTS + 1):
            self._validate_url(current_url)

            response = requests.get(
                current_url,
                timeout=self.timeout,
                headers={"User-Agent": "InspirationWorkspace/1.0"},
                allow_redirects=False,
                stream=True,
            )

            try:
                if response.status_code in self.REDIRECT_CODES:
                    location = response.headers.get("Location")

                    if not location:
                        raise ValueError("Redirect has no Location header.")

                    if redirect_count >= self.MAX_REDIRECTS:
                        raise ValueError("Too many redirects.")

                    current_url = urljoin(current_url, location)
                    continue

                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if "text/html" not in content_type:
                    raise ValueError("URL must return an HTML webpage.")

                content_length = response.headers.get("Content-Length")

                if content_length:
                    try:
                        if int(content_length) > self.MAX_RESPONSE_BYTES:
                            raise ValueError("Webpage exceeds the 5 MB limit.")
                    except ValueError as error:
                        if str(error) == "Webpage exceeds the 5 MB limit.":
                            raise
                        raise ValueError("Invalid Content-Length header.") from error

                chunks = []
                total_size = 0

                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue

                    total_size += len(chunk)

                    if total_size > self.MAX_RESPONSE_BYTES:
                        raise ValueError("Webpage exceeds the 5 MB limit.")

                    chunks.append(chunk)

                encoding = response.encoding or "utf-8"
                html = b"".join(chunks).decode(
                    encoding,
                    errors="replace",
                )

                return html, response.url

            finally:
                response.close()

        raise ValueError("Too many redirects.")

    def extract_content(self, url: str) -> dict:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        try:
            html, final_url = self._download_page(url.strip())

            soup = BeautifulSoup(html, "html.parser")

            for element in soup.select(
                "script, style, nav, footer, header, "
                "aside, form, noscript, svg"
            ):
                element.decompose()

            title = (
                soup.title.get_text(strip=True)
                if soup.title
                else ""
            )

            content_area = (
                soup.find("article")
                or soup.find("main")
                or soup.body
                or soup
            )

            extracted_text = content_area.get_text(
                separator=" ",
                strip=True,
            )

            if not extracted_text:
                raise ValueError("No readable text found on webpage.")

            return {
                "title": title,
                "url": final_url,
                "text": extracted_text,
                "character_count": len(extracted_text),
                "word_count": len(extracted_text.split()),
            }

        except (ValueError, requests.RequestException):
            raise

        except Exception as error:
            raise RuntimeError(
                f"Failed to retrieve webpage content: {error}"
            ) from error
