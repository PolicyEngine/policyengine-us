#!/usr/bin/env python
"""
Generic test runner that can split tests into batches for memory management.
Can be used for any test folder with configurable batch count.
"""

import subprocess
import sys
import os
import gc
import time
import argparse
import re
import select
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor
from concurrent.futures import wait as futures_wait
from pathlib import Path
from typing import List, Dict, Optional


def count_yaml_files(directory: Path) -> int:
    """Count YAML files in a directory recursively."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.yaml")))


def batch_cost(batch_paths: List[str]) -> int:
    """Estimated batch cost: total YAML files across the batch's paths."""
    return sum(
        count_yaml_files(Path(p)) if Path(p).is_dir() else 1 for p in batch_paths
    )


def _read_vm_hwm_mb(pid: int) -> Optional[float]:
    """Peak RSS (VmHWM high-water mark) of a live process, in MB.

    Linux-only: /proc does not exist on macOS, and the entry disappears
    once the pid is reaped — both cases return None.
    """
    try:
        with open(f"/proc/{pid}/status") as status_file:
            for line in status_file:
                if line.startswith("VmHWM:"):
                    # Format: "VmHWM:    123456 kB"
                    return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _format_rss(peak_rss_mb: Optional[float]) -> str:
    return f"{peak_rss_mb:.0f} MB" if peak_rss_mb is not None else "n/a"


def split_into_batches(
    base_path: Path,
    num_batches: int,
    exclude: List[str] = None,
    mode: str = "auto",
) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Special handling for baseline tests to separate states.
    Special handling for contrib tests to divide by folder count.

    Args:
        base_path: Path to the test directory
        num_batches: Number of batches to split into
        exclude: List of directory names to exclude (for contrib tests)
        mode: Batching mode. "auto" (default) uses the per-path heuristics
            below. "per-subdir" runs each immediate subdir as its own batch
            with loose yamls collected into a trailing batch. "per-file"
            runs every yaml (recursively) as its own batch.
    """
    if exclude is None:
        exclude = []

    # Explicit modes — bypass the per-path auto heuristics so new files
    # added to the target auto-route without a Makefile edit.
    if mode == "per-file":
        return [[str(f)] for f in sorted(base_path.rglob("*.yaml"))]

    if mode == "per-subdir":
        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = sorted(base_path.glob("*.yaml"))
        batches = [[str(s)] for s in subdirs]
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for contrib tests - one batch per heavy folder.
    # Only apply to policy/contrib (structural tests), not baseline/contrib.
    #
    # Prior grouping (3 folders per batch) pushed peak memory to ~8-9 GB
    # per subprocess, which OOMs the 16 GB ubuntu-latest runner once
    # policyengine-core 3.24+ overhead is added, surfacing as
    # "The runner has received a shutdown signal" mid-batch. Giving each
    # heavy folder its own batch keeps peaks under ~5 GB and eliminates
    # the intermittent failures without reducing total coverage.
    if str(base_path).endswith("policy/contrib"):
        # Heavy folders each get their own batch (~3-5 GB peak each) so
        # a single subprocess doesn't exceed the 16 GB runner cap.
        HEAVY = {
            "federal",
            "harris",
            "treasury",
            "ctc",
            "snap_ea",
            "ubi_center",
            "deductions",
            "aca",
            "snap",
            "tax_exempt",
            "eitc",
            "crfb",
            "congress",
        }
        # Some folders contain individual YAMLs that are each expensive
        # enough to need their own subprocess.
        PER_FILE = {"refundable_credit_conversion"}

        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = sorted(base_path.glob("*.yaml"))

        # One batch per file for per-file folders, then one batch per
        # heavy subdir (if present).
        batches = [
            [str(file)]
            for subdir in subdirs
            if subdir.name in PER_FILE
            for file in sorted(subdir.rglob("*.yaml"))
        ]
        batches += [[str(subdir)] for subdir in subdirs if subdir.name in HEAVY]

        # Catch-all batch for everything else — light subdirs and root
        # yaml files. Auto-collects any newly added folders/files so
        # they're exercised without extra config.
        light_paths = [
            str(subdir)
            for subdir in subdirs
            if subdir.name not in HEAVY and subdir.name not in PER_FILE
        ] + [str(f) for f in root_files]
        if light_paths:
            batches.append(light_paths)

        return batches

    # Special handling for contrib/states - each subfolder is its own batch
    # to allow garbage collection between state tests
    # Memory usage per state varies significantly (1.3 GB - 5.2 GB measured)
    # Note: contrib/congress runs all together (~6.3 GB total, under 7 GB limit)
    if str(base_path).endswith("contrib/states"):
        # States whose reform YAMLs are heavy enough that running the folder's
        # files together in one subprocess stacks their peaks past the 16 GB
        # runner cap → OOM ("runner received a shutdown signal"). Each
        # force-applied reform deepcopies the full parameter tree (~4-5 GB
        # peak/case, see #8559); isolating per-file frees each peak between
        # files. RI is the worst offender — its ctc_reform_test.yaml sweeps
        # ~66 reform combinations and previously OOMed shard-2 mid-run when it
        # shared a subprocess with exemption_reform_test.yaml. OH's folder
        # measured 12.4 GB as one batch on CI (run 28698452678).
        PER_FILE_STATES = {"oh", "ri"}

        subdirs = sorted([item for item in base_path.iterdir() if item.is_dir()])
        batches = []
        for subdir in subdirs:
            if subdir.name in PER_FILE_STATES:
                # One batch per YAML so each file gets a fresh subprocess.
                batches.extend([str(f)] for f in sorted(subdir.rglob("*.yaml")))
            else:
                # Each state folder becomes its own batch.
                batches.append([str(subdir)])

        # Also include any root-level YAML files as a separate batch
        root_files = sorted(list(base_path.glob("*.yaml")))
        if root_files:
            batches.append([str(file) for file in root_files])

        return batches if batches else [[str(base_path)]]

    # Special handling for reform tests - one batch per file. Reforms are
    # force-applied and deepcopy the full parameter tree (~5.5 GB peak/file
    # for ctc_linear_phase_out and winship, measured); running all files in
    # one subprocess stacks past the 16 GB runner cap → "runner received a
    # shutdown signal". A fresh subprocess per file frees each peak between
    # files.
    if "reform" in str(base_path):
        return [[str(f)] for f in sorted(base_path.rglob("*.yaml"))]

    # Special handling for states directory - support excluding specific states
    # and splitting into multiple sequential batches for memory management
    if str(base_path).endswith("gov/states"):
        subdirs = sorted(
            [
                item
                for item in base_path.iterdir()
                if item.is_dir() and item.name not in exclude
            ]
        )
        # Root-level YAML files (e.g. cross-state filing-status test) are
        # state-agnostic and would be invisible to subdir-based batching
        # otherwise — collect them into a dedicated trailing batch.
        root_files = sorted(base_path.glob("*.yaml"))

        if not subdirs and not root_files:
            return []
        # Split into num_batches sequential groups
        if num_batches > 1:
            chunk_size = len(subdirs) // num_batches
            remainder = len(subdirs) % num_batches
            batches = []
            start = 0
            for i in range(num_batches):
                end = start + chunk_size + (1 if i < remainder else 0)
                batch = [str(s) for s in subdirs[start:end]]
                if batch:
                    batches.append(batch)
                start = end
            if root_files:
                batches.append([str(f) for f in root_files])
            return batches
        batches = []
        if subdirs:
            batches.append([str(subdir) for subdir in subdirs])
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for baseline tests
    if "baseline" in str(base_path) and str(base_path).endswith("baseline"):
        states_path = base_path / "gov" / "states"

        # If --exclude states, skip states and run everything else
        # Split into memory-aware batches to prevent OOM on CI (~7 GB limit)
        # Measured peak memory per gov/ subfolder (individual runs):
        #   irs: 4.4 GB, ssa: 4.0 GB, simulation: 4.0 GB,
        #   usda: 3.0 GB, hhs: 2.7 GB, local: 2.3 GB,
        #   others: ~1.3-1.7 GB each
        if "states" in exclude:
            gov_path = base_path / "gov"

            # One batch per heavy gov/ folder (~3-4 GB peak each) so no
            # subprocess exceeds ~5 GB. Grouping previously-paired folders
            # (usda+hhs) pushed peak memory past the 16 GB runner cap once
            # policyengine-core 3.24+ overhead landed.
            HEAVY = ["irs", "ssa", "simulation", "usda", "hhs"]

            def collect_gov_paths(folder_names):
                """Collect paths for specific gov/ subfolders."""
                paths = []
                for name in folder_names:
                    p = gov_path / name
                    if p.exists():
                        paths.append(str(p))
                return paths

            # Collect remaining gov/ subfolders and files
            remaining = []
            heavy_set = set(HEAVY)
            for gov_item in gov_path.iterdir():
                if gov_item.is_dir():
                    if gov_item.name not in heavy_set and gov_item.name != "states":
                        remaining.append(str(gov_item))
                elif gov_item.suffix == ".yaml":
                    remaining.append(str(gov_item))

            # Add non-gov directories and root YAML files
            for item in base_path.iterdir():
                if item.is_dir():
                    if item.name in ["household", "contrib", "gov"]:
                        continue
                    remaining.append(str(item))
                elif item.suffix == ".yaml":
                    remaining.append(str(item))

            # Build batches (only include non-empty ones)
            batches = []
            for folder_name in HEAVY:
                paths = collect_gov_paths([folder_name])
                if paths:
                    batches.append(paths)
            if remaining:
                batches.append(remaining)

            return batches

    # Default: honor num_batches and exclude generically. The cheapest
    # common case (no chunking, no exclusion) returns the base_path as a
    # single batch so policyengine-core walks the tree once. Otherwise we
    # enumerate explicit paths — necessary because the test runner has no
    # way to skip excluded subpaths on its own, and because splitting into
    # multiple subprocesses requires discrete path lists.
    if num_batches <= 1 and not exclude:
        return [[str(base_path)]]

    if exclude:
        # Exclude applies to immediate children by name (same semantics as
        # the special-branch excludes above). Previously, `--exclude` in
        # the default branch was silently ignored, causing duplicated
        # work — e.g. `ny --exclude tax` still re-ran every `tax/*` test.
        paths = sorted(
            str(item)
            for item in base_path.iterdir()
            if (item.is_dir() or item.suffix == ".yaml") and item.name not in exclude
        )
    else:
        paths = sorted(str(f) for f in base_path.rglob("*.yaml"))

    if not paths:
        return []

    if num_batches <= 1:
        return [paths]

    chunk_size = len(paths) // num_batches
    remainder = len(paths) % num_batches
    batches = []
    start = 0
    for i in range(num_batches):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk = paths[start:end]
        if chunk:
            batches.append(chunk)
        start = end
    return batches


def run_batch(test_paths: List[str], batch_name: str, stream: bool = True) -> Dict:
    """Run a batch of tests in an isolated subprocess.

    With stream=True output is echoed to stdout in real time (sequential
    mode). With stream=False output is buffered and returned under the
    "output" key so a concurrent caller can print the whole batch
    atomically once it finishes.
    """

    python_exe = sys.executable

    buf: List[str] = []

    def emit(text: str, end: str = "\n") -> None:
        if stream:
            print(text, end=end, flush=True)
        else:
            buf.append(text + end)

    start_time = time.time()
    last_output_time = start_time
    last_heartbeat_time = start_time
    heartbeat_interval = 30
    peak_rss_mb = None
    last_rss_sample = 0.0

    # Build command - direct policyengine-core with timeout protection
    cmd = (
        [
            python_exe,
            "-m",
            "policyengine_core.scripts.policyengine_command",
            "test",
        ]
        + test_paths
        + ["-c", "policyengine_us"]
    )

    emit(f"    Running {batch_name}...")
    emit(f"    Paths: {len(test_paths)} items")
    emit("")

    # Use Popen for more control over process lifecycle
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )

    def sample_rss() -> None:
        # VmHWM is monotonic, so keeping only the latest reading preserves
        # the peak; readings stop (None) once the pid is reaped or off-Linux.
        nonlocal peak_rss_mb, last_rss_sample
        rss = _read_vm_hwm_mb(process.pid)
        if rss is not None:
            peak_rss_mb = rss
        last_rss_sample = time.time()

    try:
        test_completed = False
        test_passed = False
        output_lines = []
        output_text = ""

        # Monitor output line by line
        while True:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if not ready:
                # Sample before poll(): poll() reaps the child, after which
                # /proc/<pid>/status is gone.
                sample_rss()
                poll_result = process.poll()
                if poll_result is not None:
                    # Process terminated
                    break
                now = time.time()
                # In buffered (concurrent) mode the shared heartbeat in
                # run_batches_concurrently reports liveness instead.
                if stream and now - last_heartbeat_time >= heartbeat_interval:
                    elapsed = now - start_time
                    quiet_for = now - last_output_time
                    print(
                        f"    Still running {batch_name} after "
                        f"{elapsed:.0f}s ({quiet_for:.0f}s since last output)...",
                        flush=True,
                    )
                    last_heartbeat_time = now
                # Process still running but no output
                time.sleep(0.1)
                continue

            chunk = os.read(process.stdout.fileno(), 4096)
            if not chunk:
                sample_rss()
                if process.poll() is not None:
                    break
                continue

            # Print output in real-time, including partial pytest progress
            # lines such as dots that do not end with newlines.
            line = chunk.decode(errors="replace")
            emit(line, end="")
            last_output_time = time.time()
            last_heartbeat_time = last_output_time
            output_lines.append(line)
            output_text += line
            if last_output_time - last_rss_sample >= 1.0:
                sample_rss()

            # Detect pytest completion
            # Look for patterns like "====== 5638 passed in 491.24s ======"
            # or "====== 2 failed, 5636 passed in 500s ======"
            if re.search(
                r"=+.*\d+\s+(passed|failed).*in\s+[\d.]+s.*=+",
                output_text,
            ):
                test_completed = True
                # Check if tests passed by parsing actual failure count
                failed_match = re.search(r"(\d+) failed", output_text)
                if failed_match:
                    failed_count = int(failed_match.group(1))
                    test_passed = failed_count == 0
                else:
                    # No "X failed" in line means all passed
                    test_passed = True

                emit(f"\n    Tests completed, terminating process...")

                # Give 1 second grace period for cleanup
                time.sleep(1)
                # Final sample while the pid still exists — captures the
                # end-of-run high-water mark.
                sample_rss()

                # Terminate the process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it won't terminate
                    emit(f"    Force killing process...")
                    process.kill()
                    process.wait()
                break

        # If we didn't detect completion, wait for process with timeout
        if not test_completed:
            try:
                # Wait up to 30 minutes total
                elapsed = time.time() - start_time
                remaining_timeout = max(1800 - elapsed, 1)
                process.wait(timeout=remaining_timeout)
            except subprocess.TimeoutExpired:
                emit(f"\n    ⏱️ Timeout - terminating process...")
                sample_rss()
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                elapsed = time.time() - start_time
                return {
                    "elapsed": elapsed,
                    "status": "timeout",
                    "peak_rss_mb": peak_rss_mb,
                    "output": "".join(buf),
                }

        elapsed = time.time() - start_time

        if test_completed:
            emit(
                f"\n    Batch completed in {elapsed:.1f}s "
                f"(peak RSS: {_format_rss(peak_rss_mb)})"
            )
            return {
                "elapsed": elapsed,
                "status": "passed" if test_passed else "failed",
                "peak_rss_mb": peak_rss_mb,
                "output": "".join(buf),
            }
        else:
            # Process ended without detecting test completion
            returncode = process.poll()
            emit(
                f"\n    Batch completed in {elapsed:.1f}s "
                f"(peak RSS: {_format_rss(peak_rss_mb)})"
            )
            return {
                "elapsed": elapsed,
                "status": "passed" if returncode == 0 else "failed",
                "peak_rss_mb": peak_rss_mb,
                "output": "".join(buf),
            }

    except Exception as e:
        elapsed = time.time() - start_time
        emit(f"\n    ❌ Error: {str(e)[:100]}")

        # Clean up process if still running
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
                process.wait()
            except:
                pass

        return {
            "elapsed": elapsed,
            "status": "error",
            "peak_rss_mb": peak_rss_mb,
            "output": "".join(buf),
        }


def run_batches_concurrently(batches: List[List[str]], workers: int) -> List:
    """Run batches in a thread pool, longest-first.

    Each batch is still its own policyengine_command subprocess; the
    threads only monitor them. Output is buffered per batch and printed
    atomically (header/body/footer) when the batch finishes — only this
    (main) thread prints, so concurrent logs never interleave. A shared
    heartbeat line reports in-flight batches every ~60s.

    Returns [(batch_name, result_dict), ...] ordered by batch index.
    """
    total = len(batches)
    # Longest-first (estimated by YAML file count) so the biggest batches
    # start immediately and cannot serialize at the tail of the run.
    order = sorted(
        enumerate(batches, 1),
        key=lambda indexed: batch_cost(indexed[1]),
        reverse=True,
    )

    in_flight: Dict[str, float] = {}
    in_flight_lock = threading.Lock()

    def run_one(idx: int, batch_paths: List[str]) -> Dict:
        name = f"Batch {idx}"
        with in_flight_lock:
            in_flight[name] = time.time()
        try:
            return run_batch(batch_paths, name, stream=False)
        finally:
            with in_flight_lock:
                in_flight.pop(name, None)

    print(
        f"\nRunning {total} batches with {workers} workers "
        f"(longest first; output buffered per batch)",
        flush=True,
    )

    results: Dict[int, Dict] = {}
    heartbeat_interval = 60
    last_heartbeat = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_info = {
            executor.submit(run_one, idx, batch_paths): (idx, batch_paths)
            for idx, batch_paths in order
        }
        pending = set(future_info)
        while pending:
            done, pending = futures_wait(
                pending, timeout=5, return_when=FIRST_COMPLETED
            )
            for future in done:
                idx, batch_paths = future_info[future]
                try:
                    result = future.result()
                except Exception as e:
                    # run_batch catches its own errors; this guards the
                    # thin wrapper so one crashed worker cannot hang the
                    # run or skip the summary.
                    result = {
                        "elapsed": 0.0,
                        "status": "error",
                        "peak_rss_mb": None,
                        "output": f"Worker crashed: {str(e)[:200]}\n",
                    }
                results[idx] = result
                print(f"\n[Batch {idx}/{total}] {' '.join(batch_paths)}")
                print("-" * 60)
                print(result.get("output", ""), end="")
                print(
                    f"\n[Batch {idx}/{total}] finished in "
                    f"{result['elapsed']:.1f}s | peak RSS: "
                    f"{_format_rss(result.get('peak_rss_mb'))} | "
                    f"{result['status']}",
                    flush=True,
                )
            now = time.time()
            if pending and now - last_heartbeat >= heartbeat_interval:
                with in_flight_lock:
                    running = ", ".join(
                        f"{name} ({now - started:.0f}s)"
                        for name, started in sorted(
                            in_flight.items(), key=lambda item: item[1]
                        )
                    )
                print(
                    f"[heartbeat] {len(pending)} batches outstanding; "
                    f"in flight: {running or 'none'}",
                    flush=True,
                )
                last_heartbeat = now

    return [(f"Batch {idx}", results[idx]) for idx in sorted(results)]


def main():
    """Main entry point for the generic test runner."""

    parser = argparse.ArgumentParser(
        description="Run tests in batches with memory cleanup between batches"
    )
    parser.add_argument("test_path", help="Path to the test directory")
    parser.add_argument(
        "--batches",
        type=int,
        default=2,
        help="Number of batches to split tests into (default: 2)",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated list of directory names to exclude (for contrib tests)",
    )
    parser.add_argument(
        "--shard",
        type=str,
        default=None,
        help="Run a shard of the batches across parallel CI runners (format: 'I/N'; 1-indexed)",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "per-subdir", "per-file"],
        default="auto",
        help="Batching mode. 'per-subdir' = each immediate subdir is its own batch; 'per-file' = each yaml is its own batch.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of batches to run concurrently (default: 1 = sequential)",
    )

    args = parser.parse_args()
    exclude_list = [x.strip() for x in args.exclude.split(",") if x.strip()]

    shard_idx = shard_count = None
    if args.shard:
        try:
            shard_idx, shard_count = (int(x) for x in args.shard.split("/"))
        except ValueError:
            print(f"Error: --shard must be in format 'I/N' (got {args.shard!r})")
            sys.exit(1)
        if not (1 <= shard_idx <= shard_count):
            print(f"Error: --shard I must satisfy 1 <= I <= N (got {args.shard!r})")
            sys.exit(1)

    if args.workers < 1:
        print(f"Error: --workers must be >= 1 (got {args.workers})")
        sys.exit(1)

    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    test_path = Path(args.test_path)
    if not test_path.exists():
        print(f"Error: Test path does not exist: {args.test_path}")
        sys.exit(1)

    print(f"PolicyEngine Test Runner")
    print("=" * 60)
    print(f"Test path: {test_path}")
    print(f"Requested batches: {args.batches}")
    if args.workers > 1:
        print(f"Workers: {args.workers}")
    if exclude_list:
        print(f"Excluding: {', '.join(exclude_list)}")

    # Count total tests
    total_tests = count_yaml_files(test_path)
    print(f"Total test files: {total_tests}")

    # Split into batches
    batches = split_into_batches(test_path, args.batches, exclude_list, args.mode)

    # Apply sharding: slice every Nth batch starting from the shard index.
    # Alphabetical subfolder ordering means new folders auto-distribute by
    # position rather than requiring manual re-assignment per runner.
    if shard_count is not None:
        all_batch_count = len(batches)
        is_states = str(test_path).endswith("contrib/states")

        def _is_ri(batch):
            # A batch belongs to RI if its path's state component (the segment
            # right after contrib/states) is "ri". Works for both the per-file
            # RI batches (.../states/ri/ctc_reform_test.yaml) and any folder
            # batch (.../states/ri).
            parts = Path(batch[0]).parts
            if "states" not in parts:
                return False
            i = parts.index("states")
            return len(parts) > i + 1 and parts[i + 1] == "ri"

        ri_batches = [b for b in batches if _is_ri(b)] if is_states else []
        batches = batches[shard_idx - 1 :: shard_count]
        if ri_batches:
            # RI's CTC reform sweeps ~66 parameter combinations, each cloning
            # the full tax-benefit system — far heavier than any other state,
            # and its files are isolated per-file above. In the plain
            # alphabetical stride RI lands on a shard with other heavy states
            # (ny, ct, ut), unbalancing the contrib stage. Relocate all RI
            # batches to the last shard; every other state keeps its
            # positional assignment. (Same spirit as the NY split in the
            # Makefile.)
            batches = [b for b in batches if not _is_ri(b)]
            if shard_idx == shard_count:
                batches = batches + ri_batches
        print(
            f"Sharding: running shard {shard_idx}/{shard_count} "
            f"({len(batches)} of {all_batch_count} batches)"
        )

    if len(batches) != args.batches:
        print(f"Actual batches: {len(batches)} (optimized for {total_tests} files)")
    else:
        print(f"Actual batches: {len(batches)}")
    print("=" * 60)

    # Run batches
    run_start = time.time()
    if args.workers > 1:
        results = run_batches_concurrently(batches, args.workers)
    else:
        results = []
        for i, batch_paths in enumerate(batches, 1):
            print(f"\n[Batch {i}/{len(batches)}]")

            # Show what's in this batch
            print(f"  Test files: ~{batch_cost(batch_paths)}")
            print("-" * 60)

            result = run_batch(batch_paths, f"Batch {i}")
            results.append((f"Batch {i}", result))

            # Memory cleanup after each batch
            print("  Cleaning up memory...")
            gc.collect()

    all_failed = any(result["status"] != "passed" for _, result in results)
    total_elapsed = sum(result["elapsed"] for _, result in results)

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {total_tests}")
    for name, result in results:
        print(
            f"  {name}: {result['elapsed']:.1f}s | "
            f"peak RSS: {_format_rss(result.get('peak_rss_mb'))} | "
            f"{result['status']}"
        )
    print(f"Workers: {args.workers}")
    print(f"Total time: {total_elapsed:.1f}s")
    if args.workers > 1:
        print(f"Wall time: {time.time() - run_start:.1f}s")

    # Exit code
    sys.exit(1 if all_failed else 0)


if __name__ == "__main__":
    main()
