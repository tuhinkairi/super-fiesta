
from context_aware_suggestion_rag import utils


EXPECTED_EXPORTS = [
    "sanitize_filename",
    "calculate_file_hash",
    "read_text_file",
    "write_text_file",
    "create_directory",
    "list_files",
    "parse_url",
    "build_url",
    "is_public_ip_address",
    "create_http_client",
    "exponential_backoff",
    "retry_call",
    "retry",
    "retrying_iterator",
    "retry_statistics",
    "run_with_timeout",
    "retry_async_call",
    "async_retry",
    "gather_with_concurrency",
    "run_tasks",
    "cancel_tasks",
    "wait_for_tasks",
]

for name in EXPECTED_EXPORTS:
    assert hasattr(utils, name), f"Missing utility export: {name}"

print(f"Utility exports checked: {len(EXPECTED_EXPORTS)}")
print("All extended utility export tests passed.")
