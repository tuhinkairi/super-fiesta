import re


class TextCleaner:
    """Cleans and normalizes extracted document text."""

    def clean(self, text: str) -> str:
        """Normalize extracted text while preserving paragraphs."""

        if not isinstance(text, str):
            raise TypeError(
                "Input text must be a string."
            )

        if not text.strip():
            raise ValueError(
                "Cannot clean empty text."
            )

        # Remove null characters.
        text = text.replace("\x00", "")

        # Normalize Windows and old Mac line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove unwanted control characters,
        # while preserving newlines and tabs.
        text = "".join(
            character
            for character in text
            if character in "\n\t"
            or ord(character) >= 32
        )

        # Replace multiple horizontal spaces with one space.
        text = re.sub(r"[ \t]+", " ", text)

        # Remove spaces around line breaks.
        text = re.sub(r" *\n *", "\n", text)

        # Limit excessive blank lines to two.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
