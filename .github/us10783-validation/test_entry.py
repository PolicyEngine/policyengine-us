"""Check platform decisions with inert data and compare the preserved source AST."""

import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
DENIED = []


def audit(event, arguments):
    forbidden = event in {
        "subprocess.Popen",
        "os.system",
        "os.posix_spawn",
        "os.kill",
        "os.killpg",
        "socket.connect",
    }
    if event == "import" and arguments[0].split(".")[0] in {
        "policyengine_us",
        "policyengine_core",
    }:
        forbidden = True
    if forbidden:
        DENIED.append(event)
        raise RuntimeError(
            "Pure checks prohibit model imports and process/network actions"
        )


sys.addaudithook(audit)
import remote


class Decisions(unittest.TestCase):
    def test_download_plan_limits_the_entire_transfer_without_executing_it(self):
        argv = remote.download_plan(
            "https://nonexistent.invalid/mock-release",
            Path("/nonexistent-download"),
            10,
        )
        self.assertEqual(argv[:2], ["curl", "--disable"])
        self.assertEqual(argv[argv.index("--max-time") + 1], "10")
        self.assertNotIn("--retry", argv)
        self.assertEqual(argv[argv.index("--proto") + 1], "=https")
        for seconds in (0, -1, 31, float("inf"), float("nan")):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                remote.download_plan(
                    "https://nonexistent.invalid/mock-release",
                    Path("/nonexistent-download"),
                    seconds,
                )

    def test_stream_verification_checks_the_deadline_after_each_chunk(self):
        class MockReader:
            calls = 0

            def read(self, maximum):
                self.calls += 1
                return b"MOCK_CHUNK"

        reader = MockReader()
        ticks = iter((0, 0, 0, 2))
        with self.assertRaises(TimeoutError):
            remote.stream_digest(reader, 1, clock=lambda: next(ticks))
        self.assertEqual(reader.calls, 2)
        with self.assertRaises(TimeoutError):
            remote.stream_digest(io.BytesIO(b"MOCK_BYTES"), 1, clock=lambda: 2)
        self.assertEqual(
            remote.stream_digest(io.BytesIO(b"MOCK_BYTES"), 1, clock=lambda: 0),
            hashlib.sha256(b"MOCK_BYTES").hexdigest(),
        )

    def test_failure_resource_records_do_not_invent_final_peaks(self):
        mock_snapshot = {"memory.peak": "123", "memory.events": "oom_kill 0"}
        observed = remote.resource_record("final", mock_snapshot)
        normal = {"OOMKilled": False, "ExitCode": 0, "Running": False}
        self.assertEqual(
            remote.final_resource_record(observed, normal)["snapshot"], mock_snapshot
        )
        for state in (
            {"OOMKilled": True, "ExitCode": 137, "Running": False},
            {"OOMKilled": False, "ExitCode": 137, "Running": False},
        ):
            result = remote.final_resource_record(observed, state)
            self.assertEqual(result["status"], "UNAVAILABLE")
            self.assertIsNone(result["snapshot"])
            self.assertEqual(result["docker_state"], state)
        absent = remote.final_resource_record(None, normal)
        self.assertEqual(absent["status"], "UNAVAILABLE")
        self.assertIsNone(absent["snapshot"])
        unavailable = remote.resource_record("final", None, "MOCK_READ_FAILURE")
        self.assertEqual(
            remote.final_resource_record(unavailable, normal)["error"],
            "MOCK_READ_FAILURE",
        )

    def test_exporter_persists_start_resources_before_any_model_import(self):
        entry = functions(Path(__file__).resolve().parent / "parameter_export.py")[
            "export_entry"
        ]
        writes = [
            i
            for i, node in enumerate(entry.body)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "write_new_json"
            and isinstance(node.value.args[0], ast.Name)
            and node.value.args[0].id == "resource_start_path"
        ]
        imports = [
            i
            for i, node in enumerate(entry.body)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "importlib"
            and node.value.func.attr == "import_module"
        ]
        self.assertEqual(len(writes), 1)
        self.assertLess(writes[0], min(imports))

    def limits(self):
        return {
            "memory.max": str(remote.MEMORY),
            "memory.swap.max": "0",
            "cpu.max": "100000 100000",
            "threads": {name: "1" for name in remote.THREADS},
        }

    def context(self):
        return {
            "GITHUB_REPOSITORY": "PolicyEngine/policyengine-us",
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REF": remote.REF,
            "GITHUB_WORKFLOW_REF": "PolicyEngine/policyengine-us/.github/workflows/docs.yaml@"
            + remote.REF,
            "GITHUB_SHA": "0" * 40,
            "GITHUB_RUN_ID": "000000000000000000",
            "GITHUB_RUN_ATTEMPT": "000000000000000000",
        }

    def info(self):
        return {
            "Id": "0" * 64,
            "Image": "sha256:" + "0" * 64,
            "Config": {
                "Labels": {"us10783.run": "nonexistent-owner"},
                "User": "2147483001:2147483002",
            },
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/nonexistent-output",
                    "Destination": "/output",
                    "RW": True,
                }
            ],
            "HostConfig": {
                "Memory": remote.MEMORY,
                "MemorySwap": remote.MEMORY,
                "NanoCpus": 1_000_000_000,
                "NetworkMode": "none",
                "ReadonlyRootfs": True,
                "CapDrop": ["ALL"],
            },
        }

    def check_container(self, data):
        remote.validate_container(
            data,
            "0" * 64,
            "sha256:" + "0" * 64,
            "nonexistent-owner",
            "2147483001:2147483002",
            "/nonexistent-output",
        )

    def test_explicit_caller_user_can_write_owned_0755_output_without_extra_capabilities(
        self,
    ):
        # Nonexistent identities and command options remain inert data.
        options = remote.caller_user_options(
            2147483001, 2147483002, 2147483001, 0o40755
        )
        self.assertEqual(options, ["--user", "2147483001:2147483002"])
        for uid, gid, owner, mode in (
            (2147483001, 2147483002, 2147483003, 0o40755),
            (2147483001, 2147483002, 2147483001, 0o40555),
            (2147483001, 2147483002, 2147483001, 0o40644),
            (-1, 2147483002, 2147483001, 0o40755),
            (2147483001, 2**32 - 1, 2147483001, 0o40755),
        ):
            with (
                self.subTest(uid=uid, gid=gid, owner=owner, mode=mode),
                self.assertRaises(ValueError),
            ):
                remote.caller_user_options(uid, gid, owner, mode)
        for user in ("", "2147483003:2147483002"):
            data = self.info()
            data["Config"]["User"] = user
            with self.subTest(user=user), self.assertRaises(ValueError):
                self.check_container(data)
        for key, value in (("RW", False), ("Source", "/another-nonexistent-output")):
            data = self.info()
            data["Mounts"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check_container(data)

    def test_limits_require_memory_swap_cpu_and_serial_threads(self):
        remote.validate_limits(self.limits())
        for key, value in (
            ("memory.max", "max"),
            ("memory.max", str(remote.MEMORY + 1)),
            ("memory.swap.max", "1"),
            ("cpu.max", "max 100000"),
            ("cpu.max", "100001 100000"),
            ("cpu.max", "0 100000"),
            ("cpu.max", "1 0"),
            ("threads", {}),
        ):
            data = self.limits()
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                remote.validate_limits(data)

    def test_dispatch_context_rejects_wrong_source_workflow_or_ref(self):
        remote.validate_context(self.context())
        for key, value in (
            ("GITHUB_REPOSITORY", "nonexistent/repo"),
            ("GITHUB_EVENT_NAME", "push"),
            ("GITHUB_REF", "refs/heads/nonexistent"),
            ("GITHUB_WORKFLOW_REF", "nonexistent"),
            ("GITHUB_SHA", "missing"),
            ("GITHUB_RUN_ATTEMPT", "missing"),
        ):
            data = self.context()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                remote.validate_context(data)

    def test_container_decision_rejects_wrong_identity_or_unbounded_resources(self):
        self.check_container(self.info())
        for key, value in (
            ("Memory", 0),
            ("MemorySwap", -1),
            ("NanoCpus", 2_000_000_000),
            ("NetworkMode", "default"),
            ("ReadonlyRootfs", False),
            ("CapDrop", []),
        ):
            data = self.info()
            data["HostConfig"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check_container(data)
        for key in ("Id", "Image"):
            data = self.info()
            data[key] = "nonexistent"
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check_container(data)
        data = self.info()
        data["Config"]["Labels"]["us10783.run"] = "another-nonexistent-owner"
        with self.assertRaises(ValueError):
            self.check_container(data)

    def test_elapsed_deadline_refuses_any_launch(self):
        with self.assertRaises(TimeoutError):
            remote.remaining(-1, 600)

    def test_bootstrap_consumes_the_same_global_budget(self):
        self.assertEqual(remote.pipeline_budget(1020, 0), 870)
        self.assertEqual(remote.pipeline_budget(1020, 400), 470)
        for stop_at, now in ((0, 1), (1021, 0)):
            with self.subTest(stop_at=stop_at, now=now), self.assertRaises(ValueError):
                remote.pipeline_budget(stop_at, now)
        with self.assertRaises(TimeoutError):
            remote.pipeline_budget(1020, 900)

    def test_fixed_source_rejects_another_commit_tree_or_manifest(self):
        commit, tree = remote.SOURCES["C"]
        source = {
            "root": "/sources/C",
            "commit": commit,
            "tree": tree,
            "manifest": {"path": "/validation/evidence/C-source.json"},
        }
        remote.validate_source_record(source)
        for key in ("root", "commit", "tree"):
            data = dict(source)
            data[key] = "nonexistent"
            with self.subTest(key=key), self.assertRaises(ValueError):
                remote.validate_source_record(data)
        data = dict(source, manifest={"path": "/nonexistent-source.json"})
        with self.assertRaises(ValueError):
            remote.validate_source_record(data)

    def test_full_receipt_requires_complete_grid_fixed_source_and_original_paths(self):
        commit, tree = remote.SOURCES["C"]
        image = "sha256:" + "0" * 64
        receipt = {
            "complete": True,
            "grid_validated": True,
            "probe_only": False,
            "mode": "baseline",
            "image_id": image,
            "source": {"commit": commit, "tree": tree},
            "outputs": {
                "values": {"path": "/output/C-baseline.jsonl", "sha256": "0" * 64},
                "catalog": {
                    "path": "/output/C-baseline.jsonl.catalog.json",
                    "sha256": "0" * 64,
                },
            },
        }
        remote.validate_export_receipt(receipt, "C", "baseline", image)
        for key, value in (
            ("complete", False),
            ("grid_validated", False),
            ("probe_only", True),
            ("mode", "trustees"),
            ("image_id", "nonexistent-image"),
        ):
            data = dict(receipt)
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                remote.validate_export_receipt(data, "C", "baseline", image)
        data = dict(
            receipt,
            outputs={
                "values": {"path": "/nonexistent.jsonl", "sha256": "0" * 64},
                "catalog": receipt["outputs"]["catalog"],
            },
        )
        with self.assertRaises(ValueError):
            remote.validate_export_receipt(data, "C", "baseline", image)


def functions(path):
    return {
        node.name: node
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef)
    }


def normalized(node):
    return ast.dump(node, include_attributes=False)


def assigned(node, name):
    return isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == name for t in node.targets
    )


def slice_body(body, first, last):
    start = next(i for i, node in enumerate(body) if assigned(node, first))
    end = next(i for i, node in enumerate(body) if assigned(node, last))
    return normalized(ast.Module(body=body[start : end + 1], type_ignores=[]))


def preservation(exporter, comparator):
    root = Path(__file__).resolve().parent
    old, new = functions(exporter), functions(root / "parameter_export.py")
    kept = (
        "frozen_json",
        "verify_source",
        "verify_runtime",
        "verify_tables",
        "assert_imports",
        "selector_metadata",
    )
    for name in kept:
        if normalized(old[name]) != normalized(new[name]):
            raise ValueError("Changed protected exporter function: " + name)
    left, right = old["export_entry"].body, new["export_entry"].body
    if slice_body(left, "country", "catalog") != slice_body(
        right, "country", "catalog"
    ):
        raise ValueError("Changed real model construction or catalog traversal")
    protected = []
    history = []
    for body in (left, right):
        start = next(i for i, node in enumerate(body) if assigned(node, "by_name"))
        end = next(
            i
            for i, node in enumerate(body[start:], start)
            if isinstance(node, ast.With)
        )
        protected.append(
            normalized(ast.Module(body=body[start : end + 1], type_ignores=[]))
        )
        history_start = next(
            i for i, node in enumerate(body) if assigned(node, "history")
        )
        history.append(
            normalized(ast.Module(body=body[history_start:], type_ignores=[]))
        )
    if protected[0] != protected[1]:
        raise ValueError(
            "Changed export row traversal/validation or atomic output preparation"
        )
    if history[0] != history[1]:
        raise ValueError("Changed stated history or completion publication")
    before, after = (
        ast.parse(comparator.read_text()),
        ast.parse((root / "comparison_data.py").read_text()),
    )
    for node in ast.walk(before):
        if isinstance(node, ast.ImportFrom) and node.module == "admission_protocol":
            node.module = "atomic"
    if normalized(before) != normalized(after):
        raise ValueError("Changed frozen comparison algorithms")
    return {
        "functions_ast_equal": list(kept),
        "model_constructor_and_catalog_ast_equal": True,
        "value_traversal_ast_equal": True,
        "stated_history_and_completion_ast_equal": True,
        "comparison_module_ast_equal_except_neutral_import": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-exporter", type=Path, required=True)
    parser.add_argument("--reference-comparator", type=Path, required=True)
    args = parser.parse_args()
    proof = preservation(args.reference_exporter, args.reference_comparator)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Decisions)
    )
    modules = sorted(
        n
        for n in sys.modules
        if n == "policyengine_us"
        or n.startswith("policyengine_us.")
        or n == "policyengine_core"
        or n.startswith("policyengine_core.")
    )
    print(
        json.dumps(
            {
                "source_proof": proof,
                "tests": result.testsRun,
                "success": result.wasSuccessful(),
                "model_modules": modules,
                "denied_attempts": DENIED,
            },
            sort_keys=True,
        )
    )
    sys.exit(0 if result.wasSuccessful() and not modules and not DENIED else 1)
