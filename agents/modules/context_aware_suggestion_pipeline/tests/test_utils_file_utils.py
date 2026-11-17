import hashlib
import json
import tempfile
from pathlib import Path

from context_aware_suggestion_rag.utils.file_utils import (
    atomic_write_json,
    atomic_write_text,
    calculate_file_hash,
    copy_file,
    get_file_extension,
    get_file_size_bytes,
    read_json_file,
    read_text_file,
    sanitize_filename,
    write_json_file,
    write_text_file,
)


def test_sanitize_filename():
    assert sanitize_filename("hello/world.txt") == "hello_world.txt"
    assert sanitize_filename("CON.txt") == "_CON.txt"


def test_text_file_operations():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "sample.txt"

        write_text_file(path, "Hello World")

        assert read_text_file(path) == "Hello World"


def test_json_file_operations():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "data.json"
        data = {"name": "CreativeRAG", "version": 1}

        write_json_file(path, data)

        assert read_json_file(path) == data


def test_atomic_writes():
    with tempfile.TemporaryDirectory() as temp_dir:
        text_path = Path(temp_dir) / "atomic.txt"
        json_path = Path(temp_dir) / "atomic.json"

        atomic_write_text(text_path, "Atomic content")
        atomic_write_json(json_path, {"status": "success"})

        assert read_text_file(text_path) == "Atomic content"
        assert read_json_file(json_path) == {"status": "success"}


def test_file_hash():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "hash.txt"
        path.write_text("hello", encoding="utf-8")

        expected = hashlib.sha256(b"hello").hexdigest()

        assert calculate_file_hash(path) == expected


def test_file_metadata():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "sample.txt"
        path.write_text("hello", encoding="utf-8")

        assert get_file_extension(path) == "txt"
        assert get_file_size_bytes(path) == 5


def test_copy_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "nested" / "copy.txt"

        source.write_text("copy me", encoding="utf-8")
        result = copy_file(source, destination)

        assert result == destination
        assert destination.read_text(encoding="utf-8") == "copy me"


if __name__ == "__main__":
    tests = [
        test_sanitize_filename,
        test_text_file_operations,
        test_json_file_operations,
        test_atomic_writes,
        test_file_hash,
        test_file_metadata,
        test_copy_file,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All file utility tests passed.")
