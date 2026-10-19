
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_FILE = PROJECT_ROOT / "experiments" / "recovery_comparison.json"
ANALYSIS_FILE = PROJECT_ROOT / "experiments" / "failure_analysis.json"
OUTPUT_FILE = PROJECT_ROOT / "experiments" / "recovery_decision.json"


def choose_strategy(experiment: dict, analysis: dict) -> dict:
    """Choose a strategy using recorded experiment evidence."""
    failure = analysis["failure_analysis"]

    if not failure["failure_detected"]:
        return {
            "strategy": "none",
            "reason": "No test failure was detected.",
        }

    strategies = experiment["strategies"]
    retry = strategies["retry_without_change"]
    restore = strategies["restore_known_good_file"]

    if not retry["recovered"] and restore["recovered"]:
        return {
            "strategy": "restore_known_good_file",
            "reason": (
                "Retrying unchanged code failed, while restoring "
                "the known-good implementation passed verification."
            ),
        }

    if retry["recovered"]:
        return {
            "strategy": "retry_without_change",
            "reason": "The recorded retry passed verification.",
        }

    return {
        "strategy": "no_verified_recovery",
        "reason": (
            "The recorded strategies did not establish a successful "
            "recovery. Further diagnosis is required."
        ),
    }


def main() -> None:
    experiment = json.loads(
        EXPERIMENT_FILE.read_text(encoding="utf-8")
    )
    analysis = json.loads(
        ANALYSIS_FILE.read_text(encoding="utf-8")
    )

    decision = choose_strategy(experiment, analysis)

    record = {
        "source_experiment": experiment["experiment_id"],
        "failure_analysis": analysis["failure_analysis"],
        "decision": decision,
    }

    OUTPUT_FILE.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    print(f"Decision saved: {OUTPUT_FILE}")
    print(f"Selected strategy: {decision['strategy']}")
    print(f"Reason: {decision['reason']}")


if __name__ == "__main__":
    main()
