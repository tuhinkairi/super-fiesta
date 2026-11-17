
from pathlib import Path

from PIL import Image, UnidentifiedImageError


class ImageExtractor:
    """
    Validates images and extracts their basic metadata.
    """

    SUPPORTED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
        "GIF",
    }

    def extract_metadata(self, image_path: str | Path) -> dict:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if not path.is_file():
            raise ValueError("The provided path is not a file.")

        try:
            with Image.open(path) as image:
                image_format = image.format

                if image_format not in self.SUPPORTED_FORMATS:
                    raise ValueError(
                        f"Unsupported image format: {image_format}"
                    )

                # Verify the image can be decoded.
                image.verify()

            # Reopen after verify(), because verify() invalidates
            # the original image object for further processing.
            with Image.open(path) as image:
                return {
                    "file_name": path.name,
                    "format": image.format,
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "file_size_bytes": path.stat().st_size,
                }

        except (FileNotFoundError, ValueError):
            raise
        except (UnidentifiedImageError, OSError) as error:
            raise ValueError(
                f"Invalid or corrupted image: {error}"
            ) from error
