"""Per-subdir batching must not pack more reform combos than one subprocess holds.

The batcher's per-subdir mode gives each proposal folder its own subprocess.
A folder whose distinct reform combos exceed MAX_BATCH_COMBO_WEIGHT must be
packed by combo weight instead: policyengine-core caches one full system per
combo for the life of the subprocess, and congress/tlaib (weight 8.25) peaked
at 15.0 GB on the 16 GB CI runner at main, leaving no headroom; a branch run
of the same batch produced no output for 39 minutes before CI killed it.
"""

import importlib.util
from pathlib import Path

import yaml
import pytest

BATCHER = Path(__file__).resolve().parents[1] / "test_batched.py"
SPEC = importlib.util.spec_from_file_location("test_batched", BATCHER)
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


def _write_cases(path: Path, reforms: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cases = [
        {
            "name": f"{path.stem} {reform}",
            "period": 2026,
            "reforms": reform,
            "input": {"people": {"person": {"age": 30}}},
            "output": {"age": 30},
        }
        for reform in reforms
    ]
    path.write_text(yaml.safe_dump(cases))


def test_light_subdir_stays_one_batch(tmp_path):
    _write_cases(tmp_path / "light" / "a.yaml", ["reform_1"])
    _write_cases(tmp_path / "light" / "b.yaml", ["reform_1", "reform_2"])
    assert batched.subdir_batches(tmp_path / "light") == [[str(tmp_path / "light")]]


def test_heavy_subdir_is_packed_by_combo_weight(tmp_path):
    heavy = tmp_path / "heavy"
    _write_cases(heavy / "a.yaml", ["r1", "r2", "r3", "r4"])
    _write_cases(heavy / "b.yaml", ["r5", "r6"])
    _write_cases(heavy / "nested" / "c.yaml", ["r7"])
    _write_cases(heavy / "nested" / "d.yaml", ["r7", "r8"])
    batches = batched.subdir_batches(heavy)
    assert batches == [
        [str(heavy / "a.yaml")],
        [
            str(heavy / "b.yaml"),
            str(heavy / "nested" / "c.yaml"),
            str(heavy / "nested" / "d.yaml"),
        ],
    ]
    for batch in batches:
        combos: set = set()
        for file in batch:
            combos |= set(batched.file_reform_combos(Path(file)))
        assert batched.combo_weight(frozenset(combos)) <= batched.MAX_BATCH_COMBO_WEIGHT


def test_per_subdir_mode_splits_only_heavy_folders(tmp_path):
    _write_cases(tmp_path / "light" / "a.yaml", ["r1"])
    _write_cases(tmp_path / "heavy" / "a.yaml", ["r1", "r2", "r3", "r4"])
    _write_cases(tmp_path / "heavy" / "b.yaml", ["r5", "r6"])
    _write_cases(tmp_path / "root.yaml", ["r9"])
    batches = batched.split_into_batches(tmp_path, 2, mode="per-subdir")
    assert batches == [
        [str(tmp_path / "heavy" / "a.yaml")],
        [str(tmp_path / "heavy" / "b.yaml")],
        [str(tmp_path / "light")],
        [str(tmp_path / "root.yaml")],
    ]


def test_heavy_subdir_keeps_yml_files(tmp_path):
    heavy = tmp_path / "heavy"
    _write_cases(heavy / "a.yaml", ["r1", "r2", "r3", "r4"])
    _write_cases(heavy / "b.yaml", ["r5", "r6"])
    _write_cases(heavy / "nested" / "must_run.yml", ["r7"])
    batches = batched.subdir_batches(heavy)
    files = [file for batch in batches for file in batch]
    assert files == [
        str(heavy / "a.yaml"),
        str(heavy / "b.yaml"),
        str(heavy / "nested" / "must_run.yml"),
    ]


@pytest.mark.parametrize("mode", ["per-file", "per-subdir", "auto"])
def test_explicit_batches_keep_both_yaml_extensions(tmp_path, mode):
    _write_cases(tmp_path / "a.yaml", ["r1"])
    _write_cases(tmp_path / "b.yml", ["r2"])
    batches = batched.split_into_batches(tmp_path, 2, mode=mode)
    assert sorted(file for batch in batches for file in batch) == [
        str(tmp_path / "a.yaml"),
        str(tmp_path / "b.yml"),
    ]
    assert batched.count_yaml_files(tmp_path) == 2


@pytest.mark.parametrize(
    "relative",
    ["policy/contrib", "contrib/states", "reform", "gov/states", "arbitrary"],
)
def test_auto_path_routes_keep_root_yml_files(tmp_path, relative):
    root = tmp_path / relative
    _write_cases(root / "a.yaml", ["r1"])
    _write_cases(root / "b.yml", ["r2"])
    batches = batched.split_into_batches(root, 2)
    assert sorted(file for batch in batches for file in batch) == [
        str(root / "a.yaml"),
        str(root / "b.yml"),
    ]


def test_exclusion_preserves_yml_outside_excluded_directory(tmp_path):
    _write_cases(tmp_path / "exclude_me" / "a.yml", ["r1"])
    _write_cases(tmp_path / "b.yml", ["r2"])
    assert batched.split_into_batches(tmp_path, 2, exclude=["exclude_me"]) == [
        [str(tmp_path / "b.yml")]
    ]
