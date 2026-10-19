
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "experiments" / "recovery_comparison.json"
OUTPUT_FILE = PROJECT_ROOT / "experiments" / "failure_analysis.json"


def analyze_failure(test_output: str) -> dict:
    """Extract useful failure evidence from pytest output."""
    failed_tests = re.findall(
        r"FAILED\s+(.+?)(?:\s+-|$)",
        test_output,
        flags=re.MULTILINE,
    )

    assertion_lines = [
        line.strip()
        for line in test_output.splitlines()
        if re.search(r"\bassert\b", line)
        and ("==" in line or "!=" in line)
    ]

    return {
        "failure_detected": bool(failed_tests),
        "failed_tests": failed_tests,
        "assertion_evidence": assertion_lines,
        "raw_output_available": bool(test_output.strip()),
    }


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Experiment record not found: {INPUT_FILE}"
        )

    experiment = json.loads(
        INPUT_FILE.read_text(encoding="utf-8")
    )

    failure_output = experiment["injected_failure"]["stdout"]
    analysis = analyze_failure(failure_output)

    record = {
        "source_experiment": experiment["experiment_id"],
        "analysis_type": "pytest_output_analysis",
        "failure_analysis": analysis,
    }

    OUTPUT_FILE.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    print(f"Analysis saved: {OUTPUT_FILE}")
    print(f"Failure detected: {analysis['failure_detected']}")
    print(f"Failed tests: {analysis['failed_tests']}")
    print(f"Assertion evidence: {analysis['assertion_evidence']}")


if __name__ == "__main__":
    main()
