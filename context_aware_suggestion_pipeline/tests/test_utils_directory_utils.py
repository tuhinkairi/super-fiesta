
import tempfile
from pathlib import Path

from context_aware_suggestion_rag.utils.directory_utils import (
    count_files,
    create_directory,
    directory_exists,
    directory_size_bytes,
    ensure_directory,
    find_files_by_extension,
    get_directory_tree,
    get_relative_path,
    iter_files,
    list_files,
    remove_directory,
)


def test_create_and_ensure_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir) / "new" / "nested"

        created = create_directory(directory)

        assert created.exists()
        assert created.is_dir()
        assert ensure_directory(directory) == created


def test_list_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "one.txt").write_text("one", encoding="utf-8")
        (root / "two.json").write_text("two", encoding="utf-8")

        nested = root / "nested"
        nested.mkdir()
        (nested / "three.txt").write_text("three", encoding="utf-8")

        assert len(list_files(root)) == 2
        assert len(list_files(root, recursive=True)) == 3
        assert len(list(iter_files(root, recursive=True))) == 3


def test_find_files_by_extension():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "one.TXT").write_text("one", encoding="utf-8")
        (root / "two.json").write_text("two", encoding="utf-8")

        results = find_files_by_extension(root, ["txt", ".json"])

        assert len(results) == 2


def test_directory_size_and_count():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        (root / "one.txt").write_text("hello", encoding="utf-8")

        nested = root / "nested"
        nested.mkdir()
        (nested / "two.txt").write_text("world!", encoding="utf-8")

        assert count_files(root) == 1
        assert count_files(root, recursive=True) == 2
        assert directory_size_bytes(root) == 11


def test_directory_exists_and_tree():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        nested = root / "nested"
        nested.mkdir()
        (nested / "sample.txt").write_text("data", encoding="utf-8")

        assert directory_exists(root)

        tree = get_directory_tree(root)

        assert root.name in tree
        assert "nested" in tree[root.name]
        assert "sample.txt" in tree[root.name]["nested"]


def test_relative_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        target = root / "nested" / "file.txt"

        target.parent.mkdir()
        target.write_text("data", encoding="utf-8")

        assert get_relative_path(target, root) == Path("nested") / "file.txt"


def test_remove_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "to_remove"
        root.mkdir()
        (root / "file.txt").write_text("data", encoding="utf-8")

        assert remove_directory(root, recursive=True) is True
        assert not root.exists()


if __name__ == "__main__":
    tests = [
        test_create_and_ensure_directory,
        test_list_files,
        test_find_files_by_extension,
        test_directory_size_and_count,
        test_directory_exists_and_tree,
        test_relative_path,
        test_remove_directory,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All directory utility tests passed.")
