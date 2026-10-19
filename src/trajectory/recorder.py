
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_REPO = PROJECT_ROOT / "sandbox" / "demo_repo"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def run_command(command: list[str], cwd: Path) -> dict:
    """Run a fixed command and capture its result."""
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    return {
        "command": command,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def record_experiment() -> Path:
    """Run the demo test suite and save an experiment record."""
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    git_before = run_command(
        ["git", "status", "--short"],
        PROJECT_ROOT,
    )

    test_result = run_command(
        ["python", "-m", "pytest", "-q"],
        DEMO_REPO,
    )

    git_after = run_command(
        ["git", "status", "--short"],
        PROJECT_ROOT,
    )

    record = {
        "experiment_id": datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "working_directory": str(DEMO_REPO),
        "git_status_before": git_before["stdout"],
        "test_result": test_result,
        "git_status_after": git_after["stdout"],
        "success": test_result["return_code"] == 0,
    }

    output_path = EXPERIMENTS_DIR / "first_trajectory.json"
    output_path.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":
    saved_path = record_experiment()
    print(f"Experiment recorded: {saved_path}")
