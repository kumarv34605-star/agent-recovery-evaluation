# RETRACE
### An Evidence-Driven Framework for Evaluating Recovery Strategies in Autonomous Coding Agents

RETRACE is an experimental framework for evaluating how coding agents and automated recovery systems respond to software failures. It uses controlled fault injection, isolated workspaces, automated tests, and structured experiment records to measure whether a recovery strategy actually works.

Rather than treating a retry as a successful recovery, RETRACE records the failure, the selected recovery strategy, and the verification outcome.

## The Problem

Autonomous coding agents can make mistakes, repeat unsuccessful actions, or introduce regressions while attempting to fix software. A successful-looking action does not necessarily mean that the original problem has been resolved.

RETRACE explores an evidence-driven approach to recovery:

- Reproduce failures in controlled environments.
- Capture test failures and supporting evidence.
- Compare recovery strategies.
- Verify the result using automated tests.
- Preserve structured records for reproducibility and analysis.

## Current Implementation

The current prototype demonstrates a controlled recovery workflow using a Python calculator project.

1. Establish a passing baseline.
2. Inject a known bug into a temporary copy.
3. Run tests and record the failure.
4. Analyze the failed test and assertion evidence.
5. Compare retrying unchanged code with restoring a known-good implementation.
6. Apply a proposed text repair in an isolated workspace.
7. Run tests again and save the verification results as JSON.

### Example Experiment

The controlled experiment injects a multiplication bug that causes `multiply(4, 3)` to return `7` instead of `12`.

| Experiment | Observed result |
|---|---|
| Baseline | Tests pass |
| Injected failure | Detected |
| Retry unchanged code | Recovery fails |
| Restore known-good implementation | Recovery succeeds |
| Isolated repair validation | Tests pass |
| Original project | Remains unchanged |

These results come from the current controlled calculator experiment. They are not claims about performance on arbitrary repositories or real-world coding agents.

## Architecture

```text
Controlled Failure Injection
            |
            v
      Test Execution
            |
            v
    Failure Analysis
            |
            v
    Recovery Decision
            |
            v
   Isolated Repair / Restore
            |
            v
    Automated Verification
            |
            v
     Structured Evidence
```

## Technology Stack

- Python 3.12
- pytest
- subprocess-based test execution
- Temporary directories for isolated experiments
- JSON experiment records
- Git and GitHub

## Repository Structure

```text
RETRACE/
├── experiments/
│   ├── recovery_comparison.json
│   ├── failure_analysis.json
│   ├── recovery_decision.json
│   ├── end_to_end_recovery.json
│   └── repair_validation.json
├── sandbox/
│   └── demo_repo/
│       ├── calculator.py
│       └── test_calculator.py
├── src/
│   ├── trajectory/
│   │   └── recorder.py
│   └── recovery/
│       ├── controlled_experiment.py
│       ├── failure_analyzer.py
│       ├── recovery_planner.py
│       ├── recovery_runner.py
│       ├── repair_interface.py
│       └── demo.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12 or compatible Python version
- Git

### 1. Clone the repository

```bash
git clone https://github.com/kumarv34605-star/agent-recovery-evaluation.git
cd agent-recovery-evaluation
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an appropriate process-scoped execution policy or invoke the virtual environment's Python directly.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run the demo

```powershell
python src\recovery\demo.py
```

The demo runs the controlled experiment, failure analysis, recovery planner, end-to-end recovery workflow, and isolated repair validation.

The generated experiment records are saved in the `experiments/` directory.

### 5. Run the calculator tests independently

```powershell
python -m pytest sandbox\demo_repo -v
```

The expected baseline is three passing tests.

## Evidence and Reproducibility

RETRACE stores structured JSON records describing experiment outcomes. These records include information such as test return codes, captured output, failure evidence, selected recovery strategies, and verification results.

The prototype uses temporary copies for its controlled failure and repair demonstrations so the known-good calculator in the repository is not intentionally modified by those experiments.

## Current Limitations

- The current recovery policy is deterministic and rule-based.
- The repair demonstration uses a manually supplied text change; it does not generate repairs using an LLM.
- Experiments use a small Python calculator repository rather than a broad benchmark of real-world software projects.
- The current results establish functionality of the controlled prototype, not general recovery effectiveness.
- Model-based recovery, broader evaluation, and additional safety checks remain future work.

**Hackathon integration status:** The current local prototype does not yet demonstrate a live NVIDIA model call through Nebius Token Factory or execution on Nebius AI Cloud. That integration must be implemented and verified separately before claiming compliance with those hackathon requirements.

## Future Work

- Integrate a supported NVIDIA open-source model into the recovery loop.
- Evaluate model-proposed patches in isolated workspaces.
- Compare retry, rollback, and model-proposed repair strategies across controlled failures.
- Measure recovery success rate, regression rate, execution time, and other relevant costs.
- Expand the experiment suite and document limitations transparently.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

Developed as an experimental project exploring reliable recovery and evidence-driven evaluation for autonomous coding systems.

Repository: https://github.com/kumarv34605-star/agent-recovery-evaluation
