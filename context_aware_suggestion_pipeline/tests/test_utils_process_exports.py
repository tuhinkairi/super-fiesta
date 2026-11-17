
from context_aware_suggestion_rag import utils

EXPECTED_EXPORTS = [
    "ProcessResult",
    "run_command",
    "run_python_script",
    "command_exists",
    "get_process_output",
]

for name in EXPECTED_EXPORTS:
    assert hasattr(utils, name), f"Missing export: {name}"

print(f"Process utility exports checked: {len(EXPECTED_EXPORTS)}")
print("All process utility export tests passed.")
