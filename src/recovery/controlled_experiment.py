
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_REPO = PROJECT_ROOT / "sandbox" / "demo_repo"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def run_tests(repo_path: Path) -> dict:
    """Run pytest and capture its result and execution time."""
    started = time.perf_counter()

    result = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    return {
        "command": ["python", "-m", "pytest", "-q"],
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration_seconds": round(time.perf_counter() - started, 4),
        "passed": result.returncode == 0,
    }


def run_experiment() -> dict:
    """Inject a controlled bug and compare two recovery strategies."""
    original_calculator = DEMO_REPO / "calculator.py"
    baseline_code = original_calculator.read_text(encoding="utf-8")

    if "return a * b" not in baseline_code:
        raise ValueError(
            "Expected multiplication code was not found. "
            "Check calculator.py before running this experiment."
        )

    with tempfile.TemporaryDirectory(prefix="retrace_") as temp_dir:
        workspace = Path(temp_dir) / "demo_repo"
        shutil.copytree(DEMO_REPO, workspace)

        # Confirm that the copied project starts healthy.
        baseline = run_tests(workspace)

        if not baseline["passed"]:
            raise RuntimeError(
                "Baseline tests failed. Recovery experiment stopped."
            )

        # Inject a deliberate bug only into the temporary copy.
        calculator_path = workspace / "calculator.py"
        broken_code = baseline_code.replace(
            "return a * b",
            "return a + b",
            1,
        )
        calculator_path.write_text(broken_code, encoding="utf-8")

        failure = run_tests(workspace)

        if failure["passed"]:
            raise RuntimeError(
                "The injected bug did not cause a test failure."
            )

        # Strategy A: retry without changing the broken code.
        retry_result = run_tests(workspace)

        # Strategy B: restore the known-good calculator implementation.
        calculator_path.write_text(baseline_code, encoding="utf-8")
        restore_result = run_tests(workspace)

        return {
            "experiment_id": datetime.now(timezone.utc).isoformat(),
            "experiment": "controlled_recovery_comparison",
            "isolation": "temporary copy of demo repository",
            "baseline": baseline,
            "injected_failure": failure,
            "strategies": {
                "retry_without_change": {
                    "result": retry_result,
                    "recovered": retry_result["passed"],
                },
                "restore_known_good_file": {
                    "result": restore_result,
                    "recovered": restore_result["passed"],
                },
            },
        }


if __name__ == "__main__":
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    record = run_experiment()
    output_path = EXPERIMENTS_DIR / "recovery_comparison.json"

    output_path.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    print(f"Experiment saved: {output_path}")
    print(f"Baseline passed: {record['baseline']['passed']}")
    print(f"Injected failure detected: "
          f"{not record['injected_failure']['passed']}")

    for name, strategy in record["strategies"].items():
        print(
            f"{name}: recovered={strategy['recovered']}, "
            f"exit_code={strategy['result']['return_code']}"
        )
