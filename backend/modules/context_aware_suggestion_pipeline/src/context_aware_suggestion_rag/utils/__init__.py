
"""Public utility functions and helpers."""

from .validators import (
    validate_not_none,
    validate_non_empty_string,
    validate_identifier,
    validate_positive_integer,
    validate_non_negative_integer,
    validate_positive_number,
    validate_non_negative_number,
    validate_probability,
    validate_url,
    validate_path,
    validate_mapping,
    validate_sequence,
    validate_choice,
)

from .helpers import (
    deep_copy,
    safe_get,
    nested_get,
    nested_set,
    flatten_dict,
    chunk_sequence,
    unique_preserve_order,
    merge_dicts,
    to_json,
    from_json,
    slugify,
    truncate_text,
    get_type_name,
    is_iterable,
)

from .date_utils import (
    utc_now,
    utc_timestamp,
    ensure_aware,
    to_utc,
    to_timezone,
    parse_datetime,
    parse_date,
    datetime_to_iso,
    timestamp_to_datetime,
    datetime_to_timestamp,
    add_time,
    time_difference_seconds,
    is_expired,
    start_of_day,
    end_of_day,
    is_same_day,
    format_datetime,
)

from .formatters import (
    format_bytes,
    format_number,
    format_percentage,
    normalize_whitespace,
    format_title,
    format_snake_case,
    format_camel_case,
    format_pascal_case,
    format_list,
    format_datetime_value,
    format_mapping,
    pretty_json,
    format_metadata,
    truncate_with_ellipsis,
)

from .collections import (
    group_by,
    partition,
    chunked,
    unique_by,
    index_by,
    merge_sequences,
    flatten_one_level,
    dict_from_pairs,
    filter_mapping,
    invert_mapping,
    ensure_list,
)

from .converters import (
    to_string,
    to_integer,
    to_float,
    to_boolean,
    to_enum,
    to_list,
    to_dict,
    to_path,
    to_datetime,
    to_iso_string,
    to_json_string,
)

from .exceptions import (
    UtilityError,
    ConversionError,
    FormattingError,
    CollectionError,
    SerializationError,
    ValidationUtilityError,
    PathUtilityError,
)

from .normalizers import (
    normalize_unicode,
    normalize_keyword,
    normalize_identifier,
    normalize_metadata_keys,
    normalize_url,
    normalize_text_for_search,
    normalize_tags,
)


from .regex_utils import (
    URL_PATTERN,
    EMAIL_PATTERN,
    HASHTAG_PATTERN,
    MENTION_PATTERN,
    WORD_PATTERN,
    WHITESPACE_PATTERN,
    compile_pattern,
    extract_urls,
    extract_emails,
    extract_hashtags,
    extract_mentions,
    extract_words,
    find_all,
    contains_pattern,
    replace_pattern,
    split_by_pattern,
    remove_matches,
)


from .security_utils import (
    generate_secure_token,
    generate_secure_password,
    sha256_hash,
    sha512_hash,
    hmac_sha256,
    constant_time_compare,
    mask_string,
    mask_email,
    redact_mapping,
)

from .environment import (
    get_env,
    get_env_bool,
    get_env_int,
    get_env_float,
    get_required_env,
    get_env_list,
    get_env_mapping,
    set_env_defaults,
    load_env_file,
)

from .file_utils import (
    sanitize_filename,
    calculate_file_hash,
    read_text_file,
    write_text_file,
    read_json_file,
    write_json_file,
    atomic_write_text,
    atomic_write_json,
    get_file_extension,
    get_file_size_bytes,
    copy_file,
)

from .directory_utils import (
    create_directory,
    ensure_directory,
    list_files,
    iter_files,
    find_files_by_extension,
    directory_size_bytes,
    count_files,
    directory_exists,
    remove_directory,
    get_relative_path,
    get_directory_tree,
)

from .network_utils import (
    parse_url,
    build_url,
    add_query_params,
    get_query_params,
    validate_http_status,
    validate_json_response,
    get_response_header,
    is_host_resolvable,
    is_public_ip_address,
    create_http_client,
    create_async_http_client,
)

from .retry_utils import (
    exponential_backoff,
    retry_call,
    retry,
    retrying_iterator,
    retry_statistics,
)

from .async_utils import (
    run_with_timeout,
    retry_async_call,
    async_retry,
    gather_with_concurrency,
    run_tasks,
    cancel_tasks,
    wait_for_tasks,
)


from .process_utils import (
    ProcessResult,
    run_command,
    run_python_script,
    command_exists,
    get_process_output,
)


__all__ = [
    # Validators
    "validate_not_none",
    "validate_non_empty_string",
    "validate_identifier",
    "validate_positive_integer",
    "validate_non_negative_integer",
    "validate_positive_number",
    "validate_non_negative_number",
    "validate_probability",
    "validate_url",
    "validate_path",
    "validate_mapping",
    "validate_sequence",
    "validate_choice",

    # General helpers
    "deep_copy",
    "safe_get",
    "nested_get",
    "nested_set",
    "flatten_dict",
    "chunk_sequence",
    "unique_preserve_order",
    "merge_dicts",
    "to_json",
    "from_json",
    "slugify",
    "truncate_text",
    "get_type_name",
    "is_iterable",

    # Date utilities
    "utc_now",
    "utc_timestamp",
    "ensure_aware",
    "to_utc",
    "to_timezone",
    "parse_datetime",
    "parse_date",
    "datetime_to_iso",
    "timestamp_to_datetime",
    "datetime_to_timestamp",
    "add_time",
    "time_difference_seconds",
    "is_expired",
    "start_of_day",
    "end_of_day",
    "is_same_day",
    "format_datetime",

    # Formatters
    "format_bytes",
    "format_number",
    "format_percentage",
    "normalize_whitespace",
    "format_title",
    "format_snake_case",
    "format_camel_case",
    "format_pascal_case",
    "format_list",
    "format_datetime_value",
    "format_mapping",
    "pretty_json",
    "format_metadata",
    "truncate_with_ellipsis",

    # Collection utilities
    "group_by",
    "partition",
    "chunked",
    "unique_by",
    "index_by",
    "merge_sequences",
    "flatten_one_level",
    "dict_from_pairs",
    "filter_mapping",
    "invert_mapping",
    "ensure_list",

    # Converters
    "to_string",
    "to_integer",
    "to_float",
    "to_boolean",
    "to_enum",
    "to_list",
    "to_dict",
    "to_path",
    "to_datetime",
    "to_iso_string",
    "to_json_string",

    # Exceptions
    "UtilityError",
    "ConversionError",
    "FormattingError",
    "CollectionError",
    "SerializationError",
    "ValidationUtilityError",
    "PathUtilityError",

    # Normalizers
    "normalize_unicode",
    "normalize_keyword",
    "normalize_identifier",
    "normalize_metadata_keys",
    "normalize_url",
    "normalize_text_for_search",
    "normalize_tags",


    # Regex utilities
    "URL_PATTERN",
    "EMAIL_PATTERN",
    "HASHTAG_PATTERN",
    "MENTION_PATTERN",
    "WORD_PATTERN",
    "WHITESPACE_PATTERN",
    "compile_pattern",
    "extract_urls",
    "extract_emails",
    "extract_hashtags",
    "extract_mentions",
    "extract_words",
    "find_all",
    "contains_pattern",
    "replace_pattern",
    "split_by_pattern",
    "remove_matches",


    # Security utilities
    "generate_secure_token",
    "generate_secure_password",
    "sha256_hash",
    "sha512_hash",
    "hmac_sha256",
    "constant_time_compare",
    "mask_string",
    "mask_email",
    "redact_mapping",

    # Environment utilities
    "get_env",
    "get_env_bool",
    "get_env_int",
    "get_env_float",
    "get_required_env",
    "get_env_list",
    "get_env_mapping",
    "set_env_defaults",
    "load_env_file",

    # File utilities
    "sanitize_filename",
    "calculate_file_hash",
    "read_text_file",
    "write_text_file",
    "read_json_file",
    "write_json_file",
    "atomic_write_text",
    "atomic_write_json",
    "get_file_extension",
    "get_file_size_bytes",
    "copy_file",

    # Directory utilities
    "create_directory",
    "ensure_directory",
    "list_files",
    "iter_files",
    "find_files_by_extension",
    "directory_size_bytes",
    "count_files",
    "directory_exists",
    "remove_directory",
    "get_relative_path",
    "get_directory_tree",

    # Network utilities
    "parse_url",
    "build_url",
    "add_query_params",
    "get_query_params",
    "validate_http_status",
    "validate_json_response",
    "get_response_header",
    "is_host_resolvable",
    "is_public_ip_address",
    "create_http_client",
    "create_async_http_client",

    # Retry utilities
    "exponential_backoff",
    "retry_call",
    "retry",
    "retrying_iterator",
    "retry_statistics",

    # Async utilities
    "run_with_timeout",
    "retry_async_call",
    "async_retry",
    "gather_with_concurrency",
    "run_tasks",
    "cancel_tasks",
    "wait_for_tasks",


    # Process utilities
    "ProcessResult",
    "run_command",
    "run_python_script",
    "command_exists",
    "get_process_output",

]
