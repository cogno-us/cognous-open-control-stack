# Platform support (V1 reference)

**Supported platform: Linux only.** Owner decision D2, recorded in `process/v1-validation/v1-2026-10-16-a/preregistration.json` in cogno-us/cognous-stack-qualification before any re-run.

Why: the control plane's `BoundedRecordStore` requires Linux `flock`, and the execution runtime relies on POSIX process-group termination (`killpg`). The V1 validation executed the control plane on macOS and Windows and the Moltbot-safe runtime on Windows; those failures are retained as **unsupported-platform evidence**, not as defects, and are not counted against a Linux-supported V1.

What this does not claim: any macOS, Windows or Android support, or any C2/C3 multi-host guarantee. Hub C0 is the default (with its documented residual check-to-commit race); C1 is optional and same-host.

Evidence: qualification run 38962759690 (`results/v1-validation/v1-2026-10-16-a/final-38962759690/`). Supersedes issue #157.
