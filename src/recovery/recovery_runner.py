
import json
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from controlled_experiment import run_tests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_REPO = PROJECT_ROOT / "sandbox" / "demo_repo"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def run_recovery_workflow() -> dict:
    """Inject a bug, select a recovery, and verify it in isolation."""
    original_calculator = DEMO_REPO / "calculator.py"
    known_good_code = original_calculator.read_text(encoding="utf-8")

    if "return a * b" not in known_good_code:
        raise ValueError("Expected known-good multiply implementation.")

    with tempfile.TemporaryDirectory(prefix="retrace_") as temp_dir:
        workspace = Path(temp_dir) / "demo_repo"
        shutil.copytree(DEMO_REPO, workspace)

        baseline = run_tests(workspace)
        if not baseline["passed"]:
            raise RuntimeError("Baseline failed; workflow stopped.")

        calculator = workspace / "calculator.py"
        broken_code = known_good_code.replace(
            "return a * b", "return a + b", 1
        )
        calculator.write_text(broken_code, encoding="utf-8")

        failure = run_tests(workspace)
        if failure["passed"]:
            raise RuntimeError("Injected failure was not detected.")

        # A deterministic first policy: retrying unchanged code
        # is not useful when the same test has just failed.
        decision = {
            "strategy": "restore_known_good_file",
            "reason": (
                "The controlled test failure was detected. "
                "Retrying unchanged code cannot address this injected bug."
            ),
        }

        started = time.perf_counter()
        calculator.write_text(known_good_code, encoding="utf-8")
        recovery_duration = round(time.perf_counter() - started, 4)

        verification = run_tests(workspace)

        return {
            "experiment_id": datetime.now(timezone.utc).isoformat(),
            "workflow": "end_to_end_recovery",
            "isolation": "temporary copy; original project unchanged",
            "baseline": baseline,
            "injected_failure": failure,
            "decision": decision,
            "recovery_action": {
                "strategy": decision["strategy"],
                "duration_seconds": recovery_duration,
            },
            "verification": verification,
            "recovered": verification["passed"],
        }


def main() -> None:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    record = run_recovery_workflow()

    output_path = EXPERIMENTS_DIR / "end_to_end_recovery.json"
    output_path.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    print(f"Record saved: {output_path}")
    print(f"Baseline passed: {record['baseline']['passed']}")
    print(f"Failure detected: {not record['injected_failure']['passed']}")
    print(f"Selected strategy: {record['decision']['strategy']}")
    print(f"Final verification passed: {record['verification']['passed']}")
    print(f"Recovery successful: {record['recovered']}")


if __name__ == "__main__":
    main()
