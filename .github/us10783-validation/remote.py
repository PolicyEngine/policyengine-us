"""Run a bounded, serial parameter comparison on a task-owned Linux runner."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata as md
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import zipfile

from atomic import sha256_file, write_new_json
from comparison_data import (
    HISTORY_DATES,
    HISTORY_PATH,
    ORIGINAL_DATES,
    TRUSTEES_VIEW_YEARS,
    compare_streams,
    exact_equal,
    read_export,
    tolerance_equal,
)

REF = "refs/heads/codex/us10783-core336-validation-20261113"
SOURCES = {
    "A": (
        "3386304d28eeb148254313bc6c1b790c57749933",
        "92e6eed37b5e1ed041ffca6848bab793dbb071d9",
    ),
    "B": (
        "47c4e8720bb6ef1d5818ff026ed3d9e862e32c76",
        "bb89147a46c5a9affcb2ae7d778654c009af286b",
    ),
    "C": (
        "561afc58501cbe98a76342f1dd6377a220c5c6f2",
        "254d690fe960e58dae42ac6a43c0ab1f6f184033",
    ),
}
LOCK = "5e3c82e8f3215dd57172c81855b931cb42703e6b906b2f1c8a3003c3d462c604"
PROJECT = "a4b47e273ebcae7c4d0cee66945d151896f724e2e660a8f0ffcf35230e7bab79"
CORE = "eb7943fe5f1c63a3b70d60e673924a0703d5608dee330a4bcadb6911e0243b98"
UV = "2b428396f12572d4429cf210ca234dd599a33b3af0958a4d5ed569d63e3f344f"
MEMORY = 2 * 1024**3
ARTIFACT_LIMIT = 1024**3
HELPERS = (
    "remote.py",
    "atomic.py",
    "parameter_export.py",
    "comparison_data.py",
    "Dockerfile",
)
THREADS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def validate_limits(snapshot):
    if snapshot["memory.max"] != str(MEMORY) or snapshot["memory.swap.max"] != "0":
        raise ValueError("Require a real 2GiB cgroup with no swap")
    quota, period = snapshot["cpu.max"].split()
    if quota == "max" or not 0 < int(quota) <= int(period):
        raise ValueError("Require a positive CPU quota no greater than one CPU")
    if snapshot["threads"] != {name: "1" for name in THREADS}:
        raise ValueError("Require serial numerical-library thread limits")
    return snapshot


def resource_snapshot(deadline=None):
    root = Path("/sys/fs/cgroup")
    deadline = time.monotonic() + 2 if deadline is None else deadline
    snapshot = {}
    for name in (
        "memory.max",
        "memory.swap.max",
        "memory.peak",
        "memory.events",
        "cpu.max",
    ):
        remaining(deadline, 2)
        with (root / name).open() as stream:
            value = stream.read(16385)
        remaining(deadline, 2)
        if len(value) > 16384:
            raise ValueError("Unexpectedly large cgroup resource record")
        snapshot[name] = value.strip()
    snapshot["threads"] = {name: os.environ.get(name) for name in THREADS}
    snapshot["process_identity"] = {"uid": os.getuid(), "gid": os.getgid()}
    return validate_limits(snapshot)


def resource_record(stage, snapshot, error=None):
    return {
        "stage": stage,
        "status": "AVAILABLE" if snapshot is not None else "UNAVAILABLE",
        "snapshot": snapshot,
        "error": error,
    }


def capture_resources(stage, failure=None):
    try:
        record = resource_record(stage, resource_snapshot(time.monotonic() + 2))
    except Exception as error:
        record = resource_record(stage, None, repr(error)[:1024])
    record["export_failure"] = failure
    return record


def final_resource_record(sidecar, docker_state):
    killed = docker_state["OOMKilled"] or docker_state["ExitCode"] in (137, 143)
    if sidecar is None or killed:
        record = resource_record(
            "final", None, "No final cgroup measurement after process exit/kill"
        )
        record["last_sidecar"] = sidecar
    else:
        record = dict(sidecar)
    record["docker_state"] = docker_state
    return record


def validate_context(env):
    expected = {
        "GITHUB_REPOSITORY": "PolicyEngine/policyengine-us",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": REF,
        "GITHUB_WORKFLOW_REF": "PolicyEngine/policyengine-us/.github/workflows/docs.yaml@"
        + REF,
    }
    if any(env.get(key) != value for key, value in expected.items()):
        raise ValueError("Wrong canonical workflow dispatch identity")
    if not re.fullmatch(r"[0-9a-f]{40}", env.get("GITHUB_SHA", "")):
        raise ValueError("Missing immutable workflow SHA")
    if any(
        not re.fullmatch(r"[0-9]+", env.get(key, ""))
        for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")
    ):
        raise ValueError("Missing run identity")
    return {
        key: env[key]
        for key in (*expected, "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")
    }


def validate_source_record(source):
    sides = [side for side in SOURCES if source["root"] == "/sources/" + side]
    if len(sides) != 1 or (source["commit"], source["tree"]) != SOURCES[sides[0]]:
        raise ValueError("Source differs from the fixed A/B/C comparison")
    if (
        source["manifest"]["path"]
        != "/validation/evidence/" + sides[0] + "-source.json"
    ):
        raise ValueError("Source manifest path differs")


def validate_export_receipt(receipt, side, mode, image):
    if (
        receipt.get("complete") is not True
        or receipt.get("grid_validated") is not True
        or receipt.get("probe_only") is not False
        or receipt.get("mode") != mode
        or receipt.get("image_id") != image
        or (receipt["source"]["commit"], receipt["source"]["tree"]) != SOURCES[side]
    ):
        raise ValueError("Incomplete or misidentified full export")
    expected = {
        "values": f"/output/{side}-{mode}.jsonl",
        "catalog": f"/output/{side}-{mode}.jsonl.catalog.json",
    }
    if set(receipt["outputs"]) != set(expected):
        raise ValueError("Unexpected export output catalog")
    for key, path in expected.items():
        if receipt["outputs"][key]["path"] != path or not re.fullmatch(
            r"[0-9a-f]{64}", receipt["outputs"][key]["sha256"]
        ):
            raise ValueError("Unexpected original Linux receipt path/hash")


def caller_user_options(uid, gid, output_uid, output_mode):
    if any(
        type(value) is not int or not 0 <= value < 2**32 - 1 for value in (uid, gid)
    ):
        raise ValueError("Invalid caller UID/GID")
    if output_uid != uid or output_mode & 0o300 != 0o300:
        raise ValueError(
            "Caller must own the output directory with write/search permission"
        )
    return ["--user", f"{uid}:{gid}"]


def validate_container(info, container_id, image_id, owner, user, output_path):
    host = info["HostConfig"]
    if (
        info["Id"] != container_id
        or info["Image"] != image_id
        or info["Config"]["Labels"].get("us10783.run") != owner
        or info["Config"].get("User") != user
    ):
        raise ValueError("Container ownership/image identity changed")
    if not any(
        mount.get("Type") == "bind"
        and mount.get("Source") == output_path
        and mount.get("Destination") == "/output"
        and mount.get("RW") is True
        for mount in info.get("Mounts", [])
    ):
        raise ValueError("Container output mount differs or is read-only")
    if (
        host["Memory"] != MEMORY
        or host["MemorySwap"] != MEMORY
        or host["NanoCpus"] != 1_000_000_000
        or host["NetworkMode"] != "none"
        or not host["ReadonlyRootfs"]
        or host["CapDrop"] != ["ALL"]
    ):
        raise ValueError("Container isolation differs from the reviewed limits")


def remaining(deadline, maximum):
    seconds = min(maximum, deadline - time.monotonic())
    if seconds <= 0:
        raise TimeoutError("Global deadline reached; no retry or timeout increase")
    return seconds


def pipeline_budget(stop_at, now):
    if not 0 < stop_at - now <= 1020:
        raise ValueError("Invalid absolute job deadline")
    seconds = min(900, stop_at - now - 150)
    if seconds <= 0:
        raise TimeoutError("Bootstrap consumed the execution window")
    return seconds


def command(argv, *, timeout, cwd=None, out=None):
    return subprocess.run(
        argv,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=out or subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=out is None,
        check=True,
        timeout=timeout,
    )


def bounded_blocks(stream, deadline, clock=time.monotonic):
    while True:
        if clock() >= deadline:
            raise TimeoutError("Read deadline reached")
        block = stream.read(1024 * 1024)
        if clock() >= deadline:
            raise TimeoutError("Read deadline reached")
        if not block:
            return
        yield block


def stream_digest(stream, deadline, clock=time.monotonic):
    digest = hashlib.sha256()
    for block in bounded_blocks(stream, deadline, clock):
        digest.update(block)
    return digest.hexdigest()


def file_digest(path, deadline):
    with path.open("rb") as stream:
        return stream_digest(stream, deadline)


def download_plan(url, target, seconds):
    if not 0 < seconds <= 30:
        raise ValueError("Require a positive transfer bound no greater than 30 seconds")
    return [
        "curl",
        "--disable",
        "--fail",
        "--show-error",
        "--silent",
        "--location",
        "--proto",
        "=https",
        "--proto-redir",
        "=https",
        "--max-redirs",
        "5",
        "--max-time",
        str(seconds),
        "--output",
        str(target),
        url,
    ]


def download(url, target, expected, deadline):
    seconds = remaining(deadline, 30)
    argv = download_plan(url, target, seconds)
    with target.open("xb"):
        pass
    command(argv, timeout=remaining(deadline, seconds))
    if file_digest(target, deadline) != expected:
        raise ValueError("Downloaded release bytes differ")


def prepare(repo, build, deadline):
    build.mkdir()
    (build / "sources").mkdir()
    (build / "evidence").mkdir()
    (build / "helpers").mkdir()
    for name in HELPERS:
        shutil.copyfile(Path(__file__).parent / name, build / "helpers" / name)
    for side, (commit, tree) in SOURCES.items():
        command(
            [
                "git",
                "fetch",
                "--no-tags",
                "--depth=1",
                "https://github.com/PolicyEngine/policyengine-us.git",
                commit,
            ],
            cwd=repo,
            timeout=remaining(deadline, 90),
        )
        observed = command(
            ["git", "rev-parse", commit + "^{tree}"],
            cwd=repo,
            timeout=remaining(deadline, 10),
        ).stdout.strip()
        if observed != tree:
            raise ValueError("Source tree differs")
        catalog = command(
            ["git", "ls-tree", "-rz", commit], cwd=repo, timeout=remaining(deadline, 20)
        ).stdout
        entries = {}
        for record in catalog.split("\0"):
            if record:
                attributes, path = record.split("\t", 1)
                mode, kind, blob = attributes.split()
                if (
                    mode not in ("100644", "100755")
                    or kind != "blob"
                    or Path(path).is_absolute()
                    or ".." in Path(path).parts
                ):
                    raise ValueError("Unsupported tracked source entry")
                entries[path] = (mode, blob)
        archive = build / (side + ".tar")
        with archive.open("xb") as stream:
            command(
                ["git", "archive", "--format=tar", commit],
                cwd=repo,
                timeout=remaining(deadline, 30),
                out=stream,
            )
        if archive.stat().st_size > 512 * 1024**2:
            raise ValueError("Source archive exceeds its disk allowance")
        root = build / "sources" / side
        root.mkdir()
        with tarfile.open(archive) as stream:
            if any(not (item.isfile() or item.isdir()) for item in stream.getmembers()):
                raise ValueError("Source archive contains links or devices")
            stream.extractall(root, filter="data")
        files = {}
        actual = {
            p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
        }
        if actual != set(entries):
            raise ValueError("Tracked source catalog differs after extraction")
        for path, (mode, blob) in entries.items():
            content = (root / path).read_bytes()
            if (
                hashlib.sha1(
                    b"blob " + str(len(content)).encode() + b"\0" + content
                ).hexdigest()
                != blob
            ):
                raise ValueError("Tracked Git blob differs")
            if bool((root / path).stat().st_mode & 0o111) != (mode == "100755"):
                raise ValueError("Tracked source mode differs")
            files[path] = hashlib.sha256(content).hexdigest()
        write_new_json(
            build / "evidence" / (side + "-source.json"),
            {
                "commit": commit,
                "tree": tree,
                "files": files,
                "archive_sha256": sha256_file(archive),
            },
        )
        archive.unlink()
    if (
        sha256_file(build / "sources/C/uv.lock") != LOCK
        or sha256_file(build / "sources/C/pyproject.toml") != PROJECT
    ):
        raise ValueError("C lock/project differs")
    download(
        "https://github.com/astral-sh/uv/releases/download/0.13.4/uv-x86_64-unknown-linux-gnu.tar.gz",
        build / "uv.tar.gz",
        UV,
        deadline,
    )
    download(
        "https://files.pythonhosted.org/packages/d6/07/f0d649c065a12ca9ef35543ced8bb5b1b51bc1b2373c90c6f5c5ad39b69b/policyengine_core-3.36.0-py3-none-any.whl",
        build / "core.whl",
        CORE,
        deadline,
    )


def qualify():
    evidence = Path("/validation/evidence")
    if (
        sys.version_info[:3] != (3, 14, 7)
        or platform.machine() != "x86_64"
        or sys.platform != "linux"
    ):
        raise ValueError("Wrong Linux interpreter")
    root = Path("/sources/C")
    if (
        sha256_file(root / "uv.lock") != LOCK
        or sha256_file(root / "pyproject.toml") != PROJECT
    ):
        raise ValueError("Wrong C project metadata")
    if sha256_file(evidence / "uv.tar.gz") != UV:
        raise ValueError("Wrong pinned uv archive")
    if command(
        ["/opt/uv-x86_64-unknown-linux-gnu/uv", "--version"], timeout=10
    ).stdout.split()[:2] != ["uv", "0.13.4"]:
        raise ValueError("Wrong uv binary version")
    argv = [
        "/opt/uv-x86_64-unknown-linux-gnu/uv",
        "sync",
        "--check",
        "--dry-run",
        "--locked",
        "--offline",
        "--extra",
        "dev",
        "--no-python-downloads",
        "--python",
        sys.executable,
    ]
    check = command(argv, cwd=root, timeout=30)
    dependency = {
        "exit": check.returncode,
        "argv": argv,
        "output_sha256": hashlib.sha256(check.stdout.encode()).hexdigest(),
        "installed": sorted(
            (d.metadata["Name"], d.version) for d in md.distributions()
        ),
    }
    write_new_json(evidence / "dependencies.json", dependency)
    core = md.distribution("policyengine-core")
    country = md.distribution("policyengine-us")
    if (
        core.version != "3.36.0"
        or country.version != "2.118.10"
        or sha256_file(evidence / "core.whl") != CORE
    ):
        raise ValueError("Wrong released Core/project installation")
    direct = json.loads(country.read_text("direct_url.json"))
    if direct != {"url": root.as_uri(), "dir_info": {"editable": True}}:
        raise ValueError("Wrong editable country origin")
    matched = []
    with zipfile.ZipFile(evidence / "core.whl") as wheel:
        for name in wheel.namelist():
            if name.startswith("policyengine_core/") and not name.endswith("/"):
                expected = hashlib.sha256(wheel.read(name)).hexdigest()
                if sha256_file(core.locate_file(name)) != expected:
                    raise ValueError("Installed Core wheel bytes differ")
                matched.append({"path": name, "sha256": expected})
    if len(matched) != 195:
        raise ValueError("Incomplete Core package verification")
    core_root = Path(core.locate_file("policyengine_core")).resolve()
    if (
        sha256_file(core_root / "parameters/operations/uprate_parameters.py")
        != "21099b3aabc79777036d588d336f1b555cb649c39804e7b8437183121cd94a68"
    ):
        raise ValueError("Wrong uprating implementation")
    for name, expected in (
        ("policyengine_us", root / "policyengine_us/__init__.py"),
        ("policyengine_core", core_root / "__init__.py"),
    ):
        if Path(importlib.util.find_spec(name).origin).resolve() != expected:
            raise ValueError("Wrong cold package origin")
    if any(
        n == "policyengine_us"
        or n.startswith("policyengine_us.")
        or n == "policyengine_core"
        or n.startswith("policyengine_core.")
        for n in sys.modules
    ):
        raise ValueError("Qualification imported a model")
    qualification = {
        "status": "PASS metadata and installed bytes only",
        "core_version": core.version,
        "country_distribution_version": country.version,
        "core_files_matched": matched,
        "core_wheel_sha256": CORE,
        "lock_sha256": LOCK,
        "project_sha256": PROJECT,
        "uv_archive_sha256": UV,
        "installed_dependencies": dependency["installed"],
        "python": sys.version,
        "python_realpath": str(Path(sys.executable).resolve()),
        "machine": platform.machine(),
        "platform": platform.platform(),
    }
    write_new_json(evidence / "qualification.json", qualification)
    runtime = {
        "python_realpath": str(Path(sys.executable).resolve()),
        "prefix": sys.prefix,
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "core_root": str(core_root),
        "qualification": {
            "path": str(evidence / "qualification.json"),
            "sha256": sha256_file(evidence / "qualification.json"),
        },
        "dependency_evidence": {
            "path": str(evidence / "dependencies.json"),
            "sha256": sha256_file(evidence / "dependencies.json"),
        },
    }
    for side, (commit, tree) in SOURCES.items():
        manifest = evidence / (side + "-source.json")
        write_new_json(
            evidence / (side + "-bindings.json"),
            {
                "schema_version": 1,
                "source": {
                    "root": "/sources/" + side,
                    "commit": commit,
                    "tree": tree,
                    "manifest": {
                        "path": str(manifest),
                        "sha256": sha256_file(manifest),
                    },
                },
                "runtime": runtime,
                "tables": {
                    "dates": list(ORIGINAL_DATES),
                    "history": {HISTORY_PATH: list(HISTORY_DATES)},
                    "trustees_view_dates": [
                        f"{year}-01-01" for year in TRUSTEES_VIEW_YEARS
                    ],
                    "trustees_defaults": {
                        "start_year": 2035,
                        "end_year": 2100,
                        "projection_base_year": 2026,
                    },
                },
            },
        )


def publish_provenance():
    evidence = Path("/validation/evidence")
    for source in sorted(evidence.glob("*.json")):
        target = Path("/output") / ("runtime-" + source.name)
        if target.exists():
            if sha256_file(target) != sha256_file(source):
                raise ValueError("Published runtime provenance changed")
        else:
            with source.open("rb") as original, target.open("xb") as copy:
                shutil.copyfileobj(original, copy)


def container(argv, label, output, image, owner, deadline, maximum):
    name = "us10783-" + owner + "-" + label
    output_stat = output.stat()
    uid, gid = os.getuid(), os.getgid()
    user_options = caller_user_options(
        uid, gid, output_stat.st_uid, output_stat.st_mode
    )
    identity = {
        "caller_uid": uid,
        "caller_gid": gid,
        "container_user": user_options[1],
        "output_uid": output_stat.st_uid,
        "output_gid": output_stat.st_gid,
        "output_mode": oct(output_stat.st_mode & 0o7777),
    }
    write_new_json(output / (label + ".identity.json"), identity)
    create = [
        "docker",
        "create",
        *user_options,
        "--name",
        name,
        "--label",
        "us10783.run=" + owner,
        "--memory",
        str(MEMORY),
        "--memory-swap",
        str(MEMORY),
        "--cpus",
        "1",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--tmpfs",
        "/tmp:rw,size=67108864",
        "--mount",
        "type=bind,src=" + str(output) + ",dst=/output",
    ]
    for key in THREADS:
        create += ["--env", key + "=1"]
    create += [
        "--env",
        "US10783_IMAGE_ID=" + image,
        image,
        "/sources/C/.venv/bin/python",
        "-B",
        *argv,
    ]
    try:
        cid = command(create, timeout=remaining(deadline, 20)).stdout.strip()
    except BaseException:
        # Reconcile a timed-out Docker client before treating creation as absent.
        observed = subprocess.run(
            ["docker", "inspect", name],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        if observed.returncode == 0:
            info = json.loads(observed.stdout)[0]
            validate_container(
                info, info["Id"], image, owner, user_options[1], str(output)
            )
            if info["State"]["Running"]:
                raise RuntimeError(
                    "Unexpected running container after failed create; cleanup pending"
                )
            command(["docker", "rm", info["Id"]], timeout=10)
        write_new_json(
            output / (label + ".create-failure.json"),
            {
                "reconciled": observed.returncode == 0,
                "inspect_exit": observed.returncode,
                "model_started": False,
                "caller_and_output_identity": identity,
            },
        )
        raise
    if not re.fullmatch(r"[0-9a-f]{64}", cid):
        raise ValueError("Docker did not return an owned container ID")

    def inspect():
        info = json.loads(command(["docker", "inspect", cid], timeout=10).stdout)[0]
        validate_container(info, cid, image, owner, user_options[1], str(output))
        return info

    process = None
    failure = None
    started = time.monotonic()
    try:
        inspect()
        with (output / (label + ".log")).open("x") as log:
            process = subprocess.Popen(
                ["docker", "start", "--attach", cid],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            end = min(deadline, started + maximum)
            while process.poll() is None:
                if time.monotonic() >= end:
                    raise TimeoutError("Model or global wall deadline reached")
                if shutil.disk_usage(output).free < 1024**3:
                    raise OSError("Runner disk headroom fell below 1GiB")
                time.sleep(0.25)
            info = inspect()
            if (
                process.returncode
                or info["State"]["ExitCode"]
                or info["State"]["OOMKilled"]
            ):
                raise RuntimeError("Container failed or reached its memory cap")
    except BaseException as error:
        failure = repr(error)
        raise
    finally:
        try:
            info = inspect()
            if info["State"]["Running"]:
                command(["docker", "stop", "--time", "10", cid], timeout=15)
                info = inspect()
            if info["State"]["Running"]:
                raise RuntimeError("Owned container cleanup pending")
            if process is not None:
                process.wait(timeout=15)
            command(["docker", "rm", cid], timeout=10)
        except BaseException as cleanup_error:
            write_new_json(
                output / (label + ".container.json"),
                {
                    "id": cid,
                    "image": image,
                    "owner": owner,
                    "failure": failure,
                    "cleanup_verified": False,
                    "caller_and_output_identity": identity,
                    "cleanup_error": repr(cleanup_error),
                    "final_resources": resource_record(
                        "final", None, "Docker cleanup/inspection did not complete"
                    ),
                },
            )
            raise
        final_sidecar_path = output / (label + ".manifest.json.resources-final.json")
        sidecar = None
        sidecar_error = None
        if final_sidecar_path.exists():
            try:
                sidecar = json.loads(final_sidecar_path.read_text())
            except Exception as error:
                sidecar_error = repr(error)[:1024]
        final_resources = final_resource_record(sidecar, info["State"])
        final_resources["sidecar_read_error"] = sidecar_error
        write_new_json(output / (label + ".resources-host-final.json"), final_resources)
        write_new_json(
            output / (label + ".container.json"),
            {
                "id": cid,
                "image": image,
                "owner": owner,
                "state": info["State"],
                "caller_and_output_identity": identity,
                "inspected_user": info["Config"]["User"],
                "inspected_output_mount": [
                    mount
                    for mount in info["Mounts"]
                    if mount.get("Destination") == "/output"
                ],
                "final_resources_status": final_resources["status"],
                "limits": {
                    key: info["HostConfig"][key]
                    for key in (
                        "Memory",
                        "MemorySwap",
                        "NanoCpus",
                        "NetworkMode",
                        "ReadonlyRootfs",
                        "CapDrop",
                    )
                },
                "elapsed_seconds": time.monotonic() - started,
                "failure": failure,
                "cleanup_verified": True,
            },
        )


def compare():
    output = Path("/output")
    manifests = {}
    for side, (commit, _) in SOURCES.items():
        for mode in ("baseline", "trustees"):
            manifest, _ = read_export(output / f"{side}-{mode}.manifest.json")
            if (
                manifest["source"]["commit"] != commit
                or manifest["mode"] != mode
                or manifest.get("probe_only")
            ):
                raise ValueError("Wrong final export identity")
            manifests[side, mode] = manifest
    if len({m["runtime_binding_sha256"] for m in manifests.values()}) != 1:
        raise ValueError("Exports used different runtime bindings")
    if {m["image_id"] for m in manifests.values()} != {os.environ["US10783_IMAGE_ID"]}:
        raise ValueError("Exports used another image")
    counts = {}
    changed = {}
    with ExitStack() as stack:
        streams = {}

        def ensure(name):
            if name not in streams:
                streams[name] = stack.enter_context(
                    (output / (name + ".jsonl")).open("x")
                )
                counts[name] = 0

        def emit(name, row):
            ensure(name)
            streams[name].write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            counts[name] = counts.get(name, 0) + 1

        for mode in ("baseline", "trustees"):
            for pair in ("AC", "AB", "BC"):
                for kind in ("raw", "legacy"):
                    ensure(mode + "-" + pair + "-" + kind)
            ensure(mode + "-ABC-raw")
            ensure(mode + "-earned-history-raw")
            ensure("trustees-original12-raw")
            sides = {
                s: read_export(output / f"{s}-{mode}.manifest.json")[1] for s in SOURCES
            }
            for row in compare_streams(sides):
                values = row["sides"]
                ab, bc, ac = (
                    exact_equal(values[x], values[y])
                    for x, y in (("A", "B"), ("B", "C"), ("A", "C"))
                )
                row["attribution"] = (
                    "PR-only"
                    if ab
                    else (
                        "upstream-only"
                        if bc
                        else ("unresolved-interaction" if ac else "both")
                    )
                )
                row["catalog_addition_or_removal"] = any(
                    v["kind"] == "ABSENT_SIDE" for v in values.values()
                )
                emit(mode + "-ABC-raw", row)
                if mode == "trustees" and row["date"] in {
                    f"{y}-01-01" for y in TRUSTEES_VIEW_YEARS
                }:
                    emit("trustees-original12-raw", row)
                if row["path"] == HISTORY_PATH and row["date"] in HISTORY_DATES:
                    emit(mode + "-earned-history-raw", row)
                for x, y in (("A", "C"), ("A", "B"), ("B", "C")):
                    if not exact_equal(values[x], values[y]):
                        emit(mode + "-" + x + y + "-raw", row)
                        if not tolerance_equal(values[x], values[y]):
                            emit(mode + "-" + x + y + "-legacy", row)
        for side in SOURCES:
            ensure(side + "-baseline-trustees-raw")
            ensure(side + "-baseline-trustees-legacy")
            sides = {
                m: read_export(output / f"{side}-{m}.manifest.json")[1]
                for m in ("baseline", "trustees")
            }
            paths = set()
            for row in compare_streams(sides, allow_cross_mode=True):
                emit(side + "-baseline-trustees-raw", row)
                if not row["legacy_tolerance_equal"]:
                    emit(side + "-baseline-trustees-legacy", row)
                paths.add(row["path"])
            changed[side] = sorted(paths)
    selection = {}
    for x, y in (("A", "C"), ("A", "B"), ("B", "C")):
        selection[x + y] = {}
        for key in ("initial", "effective"):
            left, right = (
                manifests[s, "trustees"]["selectors"].get(key) for s in (x, y)
            )
            selection[x + y][key] = (
                None
                if left is None or right is None
                else {
                    "only_" + x: sorted(set(left) - set(right)),
                    "only_" + y: sorted(set(right) - set(left)),
                }
            )
        followers = [
            {
                v["path"]: v["uprating"]
                for v in manifests[s, "trustees"]["selectors"]["followers"]
            }
            for s in (x, y)
        ]
        selection[x + y]["follower_differences"] = [
            {
                "path": path,
                x: followers[0].get(path, {"kind": "ABSENT_SIDE"}),
                y: followers[1].get(path, {"kind": "ABSENT_SIDE"}),
            }
            for path in sorted(set(followers[0]) | set(followers[1]))
            if followers[0].get(path) != followers[1].get(path)
        ]
    write_new_json(
        output / "comparison.json",
        {
            "complete": True,
            "counts": counts,
            "actual_changed_paths": changed,
            "selection_symmetric_differences": selection,
            "outputs": {
                name + ".jsonl": sha256_file(output / (name + ".jsonl"))
                for name in streams
            },
            "review_required": any(m["review_required"] for m in manifests.values()),
            "parity_approved": False,
        },
    )


def package(output, artifact):
    staging = artifact.with_name(artifact.name + ".partial")
    staging.mkdir()
    records = {}
    total = 0
    deadline = time.monotonic() + 75
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.suffix not in (
            ".json",
            ".jsonl",
            ".log",
            ".partial",
        ):
            raise ValueError("Unexpected output artifact path")
        target = staging / (path.name + ".gz")
        with path.open("rb") as source, target.open("xb") as compressed:
            with gzip.GzipFile(
                filename="", mode="wb", compresslevel=1, fileobj=compressed, mtime=0
            ) as stream:
                for block in bounded_blocks(source, deadline):
                    stream.write(block)
                    if total + target.stat().st_size > ARTIFACT_LIMIT - 2 * 1024**2:
                        raise ValueError(
                            "Compressed evidence reached its upload allowance"
                        )
        total += target.stat().st_size
        if total > ARTIFACT_LIMIT:
            raise ValueError("Compressed artifacts exceed 1GiB; no upload")
        with gzip.open(target, "rb") as stream:
            digest = stream_digest(stream, deadline)
        if digest != file_digest(path, deadline):
            raise ValueError("Compressed evidence differs")
        records[target.name] = {
            "compressed_sha256": file_digest(target, deadline),
            "raw_sha256": digest,
            "compressed_bytes": target.stat().st_size,
            "raw_bytes": path.stat().st_size,
        }
    write_new_json(
        staging / "MANIFEST.json",
        {
            "files": records,
            "compressed_bytes": total,
            "six_exports_complete": (output / "exports.json").exists(),
            "parity_approved": False,
        },
    )
    staging.rename(artifact)


def run(repo, work):
    context = validate_context(os.environ)
    if (
        command(["git", "rev-parse", "HEAD"], cwd=repo, timeout=10).stdout.strip()
        != context["GITHUB_SHA"]
    ):
        raise ValueError("Checkout differs from the workflow commit")
    work.mkdir()
    output = work / "output"
    output.mkdir()
    artifact = work / "artifact"
    budget = pipeline_budget(int(os.environ["US10783_STOP_AT"]), time.time())
    deadline = time.monotonic() + budget
    owner = context["GITHUB_RUN_ID"] + "-" + context["GITHUB_RUN_ATTEMPT"]
    write_new_json(
        output / "run.json",
        {
            "github": context,
            "sources": SOURCES,
            "helpers": {n: sha256_file(Path(__file__).parent / n) for n in HELPERS},
            "pipeline_budget_seconds": budget,
            "maximum_pipeline_seconds": 900,
            "cleanup_and_packaging_reserve_seconds": 150,
            "outer_job_minutes": 20,
            "artifact_retention_days": 1,
        },
    )

    def cancelled(number, frame):
        raise InterruptedError("Runner requested cancellation")

    signal.signal(signal.SIGTERM, cancelled)
    error = None
    try:
        if shutil.disk_usage(work).free < 8 * 1024**3:
            raise OSError("Require 8GiB free before source/image preparation")
        prepare(repo, work / "build", deadline)
        with (output / "build.log").open("x") as log:
            command(
                [
                    "docker",
                    "build",
                    "--platform",
                    "linux/amd64",
                    "--iidfile",
                    str(work / "image.id"),
                    "-f",
                    str(work / "build/helpers/Dockerfile"),
                    str(work / "build"),
                ],
                timeout=remaining(deadline, 300),
                out=log,
            )
        image = (work / "image.id").read_text().strip()
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
            raise ValueError("Missing immutable image identity")
        write_new_json(
            output / "image.json",
            {"id": image, "core_wheel_sha256": CORE, "uv_archive_sha256": UV},
        )
        for side, mode in (
            ("C", "baseline"),
            ("C", "trustees"),
            ("A", "baseline"),
            ("A", "trustees"),
            ("B", "baseline"),
            ("B", "trustees"),
        ):
            label = side + "-" + mode
            commit, tree = SOURCES[side]
            argv = [
                "/validation/parameter_export.py",
                "--bindings",
                "/validation/evidence/" + side + "-bindings.json",
                "--source-sha",
                commit,
                "--tree-sha",
                tree,
                "--mode",
                mode,
                "--year-profile",
                "original26",
                "--history-path",
                HISTORY_PATH,
                "--out",
                "/output/" + label + ".jsonl",
                "--manifest-out",
                "/output/" + label + ".manifest.json",
            ]
            container(argv, label, output, image, owner, deadline, 600)
        runtime_ids = set()
        relocation = {}
        for side in SOURCES:
            for mode in ("baseline", "trustees"):
                receipt_path = output / f"{side}-{mode}.manifest.json"
                receipt = json.loads(receipt_path.read_text())
                validate_export_receipt(receipt, side, mode, image)
                runtime_ids.add(receipt["runtime_binding_sha256"])
                for record in receipt["outputs"].values():
                    target = output / Path(record["path"]).name
                    remaining(deadline, 600)
                    if file_digest(target, deadline) != record["sha256"]:
                        raise ValueError("Completed export output hash differs")
                    relocation[record["path"]] = {
                        "member": target.name + ".gz",
                        "raw_sha256": record["sha256"],
                    }
        if len(runtime_ids) != 1:
            raise ValueError("Completed exports used different runtime bindings")
        for target in output.glob("runtime-*.json"):
            original = "/validation/evidence/" + target.name.removeprefix("runtime-")
            relocation[original] = {
                "member": target.name + ".gz",
                "raw_sha256": sha256_file(target),
            }
        write_new_json(
            output / "relocation.json",
            {
                "original_linux_paths": relocation,
                "receipt_bytes_unchanged": True,
                "local_paths": None,
            },
        )
        write_new_json(
            output / "exports.json",
            {
                "status": "SIX_EXPORTS_COMPLETE",
                "parity_approved": False,
                "comparison_status": "OFFLINE_COMPARISONS_REQUIRED",
                "runtime_binding_sha256": runtime_ids.pop(),
            },
        )
    except BaseException as failure:
        error = repr(failure)
    finally:
        write_new_json(
            output / "terminal.json",
            {
                "error": error,
                "six_exports_complete": (output / "exports.json").exists(),
                "at": datetime.now(timezone.utc).isoformat(),
                "parity_approved": False,
            },
        )
        try:
            package(output, artifact)
        except BaseException as packaging_error:
            artifact.mkdir()
            write_new_json(
                artifact / "ERROR.json",
                {
                    "error": repr(packaging_error),
                    "raw_evidence_uploaded": False,
                    "complete_comparison": False,
                    "parity_approved": False,
                },
            )
            for name in ("run.json", "terminal.json"):
                shutil.copyfile(output / name, artifact / name)
            if error is None:
                error = repr(packaging_error)
    if error:
        raise RuntimeError(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "qualify", "compare"))
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.action == "qualify":
        qualify()
    elif args.action == "compare":
        compare()
    else:
        run(args.repo.resolve(), args.work.resolve())


if __name__ == "__main__":
    main()
