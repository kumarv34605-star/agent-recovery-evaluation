
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECOVERY_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def run_step(script_name: str) -> None:
    script_path = RECOVERY_DIR / script_name
    print(f"\n{'=' * 55}")
    print(f"Running: {script_name}")
    print("=" * 55)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed with exit code {result.returncode}"
        )


def main() -> None:
    # Run the experiment, analyze its evidence, and select a recovery.
    run_step("controlled_experiment.py")
    run_step("failure_analyzer.py")
    run_step("recovery_planner.py")
    run_step("recovery_runner.py")
    run_step("repair_interface.py")

    # Summarize the saved results.
    end_to_end = json.loads(
        (EXPERIMENTS_DIR / "end_to_end_recovery.json").read_text(
            encoding="utf-8"
        )
    )
    repair = json.loads(
        (EXPERIMENTS_DIR / "repair_validation.json").read_text(
            encoding="utf-8"
        )
    )

    print(f"\n{'=' * 55}")
    print("RETRACE DEMO SUMMARY")
    print("=" * 55)
    print(f"Baseline passed: {end_to_end['baseline']['passed']}")
    print(
        "Injected failure detected: "
        f"{not end_to_end['injected_failure']['passed']}"
    )
    print(f"Recovery strategy: {end_to_end['decision']['strategy']}")
    print(f"Recovery verified: {end_to_end['recovered']}")
    print(f"Repair verification passed: {repair['verification_passed']}")
    print(f"Original project modified: {repair['original_project_modified']}")
    print(f"Evidence directory: {EXPERIMENTS_DIR}")

    if not (
        end_to_end["baseline"]["passed"]
        and not end_to_end["injected_failure"]["passed"]
        and end_to_end["recovered"]
        and repair["verification_passed"]
        and not repair["original_project_modified"]
    ):
        raise SystemExit("RETRACE demo did not satisfy all checks.")

    print("\nAll demo checks passed.")


if __name__ == "__main__":
    main()
