
import json
import shutil
import tempfile
import time
from pathlib import Path

from controlled_experiment import run_tests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_REPO = PROJECT_ROOT / "sandbox" / "demo_repo"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def validate_repair(
    file_name: str,
    old_text: str,
    new_text: str,
) -> dict:
    """Apply a proposed text repair in isolation and verify it with tests."""

    if not file_name or Path(file_name).name != file_name:
        raise ValueError("Only a file name within the demo workspace is allowed.")

    if not old_text or old_text == new_text:
        raise ValueError("The repair must contain a meaningful change.")

    source_file = DEMO_REPO / file_name

    if not source_file.is_file():
        raise FileNotFoundError(f"File not found: {file_name}")

    original_code = source_file.read_text(encoding="utf-8")

    if original_code.count(old_text) != 1:
        raise ValueError(
            "The old text must match exactly once to avoid an ambiguous repair."
        )

    with tempfile.TemporaryDirectory(prefix="retrace_repair_") as temp_dir:
        workspace = Path(temp_dir) / "demo_repo"
        shutil.copytree(DEMO_REPO, workspace)

        target_file = workspace / file_name
        target_code = target_file.read_text(encoding="utf-8")
        target_file.write_text(
            target_code.replace(old_text, new_text, 1),
            encoding="utf-8",
        )

        started = time.perf_counter()
        verification = run_tests(workspace)
        duration = round(time.perf_counter() - started, 4)

        result = {
            "file": file_name,
            "verification_passed": verification["passed"],
            "test_return_code": verification["return_code"],
            "test_stdout": verification["stdout"],
            "test_stderr": verification["stderr"],
            "verification_duration_seconds": duration,
            "workspace": "temporary copy",
            "original_project_modified": False,
        }

    return result


def main() -> None:
    global DEMO_REPO

    original_demo_repo = DEMO_REPO

    try:
        # Create an isolated copy of the known-good calculator.
        with tempfile.TemporaryDirectory(prefix="retrace_demo_") as temp_dir:
            demo_repo = Path(temp_dir) / "demo_repo"
            shutil.copytree(original_demo_repo, demo_repo)

            # Inject a bug into multiplication in the temporary copy.
            calculator = demo_repo / "calculator.py"
            code = calculator.read_text(encoding="utf-8")
            calculator.write_text(
                code.replace("return a * b", "return a + b", 1),
                encoding="utf-8",
            )

            # Test the proposed repair against that same broken copy.
            DEMO_REPO = demo_repo

            result = validate_repair(
                file_name="calculator.py",
                old_text="def multiply(a, b):\n    return a + b",
                new_text="def multiply(a, b):\n    return a * b",
            )

        # Save the evidence after the temporary workspace is removed.
        EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = EXPERIMENTS_DIR / "repair_validation.json"
        output_path.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8",
        )

        print(f"Record saved: {output_path}")
        print(f"Verification passed: {result['verification_passed']}")
        print(
            f"Original project modified: "
            f"{result['original_project_modified']}"
        )

    finally:
        DEMO_REPO = original_demo_repo


if __name__ == "__main__":
    main()

