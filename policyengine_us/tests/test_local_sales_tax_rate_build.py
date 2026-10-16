"""Small source-parser/cache checks; no tax-benefit model is constructed."""

import csv
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pandas as pd
import pytest


@pytest.fixture(scope="module")
def build_script():
    path = (
        Path(__file__).resolve().parents[2] / "scripts/local_sales_tax_rates/build.py"
    )
    spec = importlib.util.spec_from_file_location("local_sales_tax_build", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cached_build(build_script, monkeypatch, tmp_path):
    monkeypatch.setattr(build_script, "BOUNDARY_CACHE", tmp_path / "cache")
    return build_script


def boundary_row(*, city="Rutland", place="61225"):
    fields = [""] * 89
    for column, value in {
        0: "A",
        1: "20220101",
        2: "29991231",
        14: city,
        15: "05701",
        22: "50",
        23: "50",
        24: "021",
        25: place,
    }.items():
        fields[column] = value
    return fields


def write_boundary(sources, rows, *, zipped=False):
    folder = sources / "sst" / "boundary"
    folder.mkdir(parents=True, exist_ok=True)
    stream = io.StringIO(newline="")
    csv.writer(stream).writerows(rows)
    path = folder / ("VTB2026Q4.zip" if zipped else "VTB2026Q4.csv")
    if zipped:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("boundary.csv", stream.getvalue().encode("latin-1"))
    else:
        path.write_text(stream.getvalue(), encoding="latin-1")
    return path


@pytest.mark.parametrize("zipped", [False, True])
def test_audit_counts_width_errors_before_selecting_columns(
    cached_build, tmp_path, zipped
):
    sources = tmp_path / "sources"
    valid = boundary_row(city="Rutland, City")
    missing_required_type = valid[:-1]
    missing_required_type[-1] = "12345"
    path = write_boundary(
        sources,
        [
            valid,
            missing_required_type,
            valid + ["unexpected"],
            valid + [""],
            valid,
            valid[:-1],
        ],
        zipped=zipped,
    )
    audits = {}
    with pytest.warns(UserWarning, match="skipped 2 malformed boundary rows"):
        frame = cached_build.load_sst_boundary(sources, "VT", audits)
    audit = audits[str(path.relative_to(sources))]
    assert audit["expected_fields"] == 89
    assert audit["input_rows"] == 6
    assert audit["accepted_rows"] == 4
    assert audit["skipped_rows"] == 2
    assert audit["trailing_blank_rows"] == 1
    assert audit["padded_trailing_type_rows"] == 1
    assert audit["skipped_row_examples"] == [
        {"line": 2, "fields": 88},
        {"line": 3, "fields": 90},
    ]
    assert audit["source_sha256"] == cached_build.sha256(path)
    assert frame.records.tolist() == [4]
    assert frame.city.tolist() == ["RUTLAND, CITY"]
    assert not (sources / "sst" / "cache").exists()


def test_cache_hit_restores_audit_without_reparsing(
    cached_build, monkeypatch, tmp_path
):
    sources = tmp_path / "sources"
    write_boundary(sources, [boundary_row(), boundary_row()[:-2], boundary_row()[:-1]])
    original = {}
    with pytest.warns(UserWarning, match="skipped 1 malformed boundary rows"):
        frame = cached_build.load_sst_boundary(sources, "VT", original)

    def unexpected_parse(*args, **kwargs):
        raise AssertionError("an input-pinned cache must avoid reparsing")

    monkeypatch.setattr(cached_build, "sst_boundary_chunks", unexpected_parse)
    restored = {}
    with pytest.warns(UserWarning, match="skipped 1 malformed boundary rows"):
        again = cached_build.load_sst_boundary(sources, "VT", restored)
    assert restored == original
    assert next(iter(restored.values()))["skipped_rows"] == 1
    assert next(iter(restored.values()))["padded_trailing_type_rows"] == 1
    pd.testing.assert_frame_equal(again, frame)
    sidecar = next(cached_build.BOUNDARY_CACHE.glob("*.audit.json"))
    metadata = json.loads(sidecar.read_text())
    assert metadata["schema_version"] == 3
    assert metadata["source_sha256"] == next(iter(original.values()))["source_sha256"]


def test_changed_input_same_filename_invalidates_cache(cached_build, tmp_path):
    sources = tmp_path / "sources"
    write_boundary(sources, [boundary_row()])
    first = {}
    cached_build.load_sst_boundary(sources, "VT", first)
    write_boundary(sources, [boundary_row(city="Rutland Town", place="61300")])
    second = {}
    frame = cached_build.load_sst_boundary(sources, "VT", second)
    assert (
        next(iter(first.values()))["source_sha256"]
        != next(iter(second.values()))["source_sha256"]
    )
    assert frame.city.tolist() == ["RUTLAND TOWN"]
    assert frame.place.tolist() == ["61300"]


def test_unaudited_v2_and_missing_sidecar_are_not_reused(cached_build, tmp_path):
    sources = tmp_path / "sources"
    write_boundary(sources, [boundary_row()])
    old_cache = sources / "sst" / "cache" / "VTB2026Q4-v2.pkl"
    old_cache.parent.mkdir(parents=True)
    pd.DataFrame({"records": [999]}).to_pickle(old_cache)
    assert cached_build.load_sst_boundary(sources, "VT").records.tolist() == [1]
    # A pre-normalization v3 audit must not preserve an obsolete row count.
    sidecar = next(cached_build.BOUNDARY_CACHE.glob("*.audit.json"))
    cache = next(cached_build.BOUNDARY_CACHE.glob("*.pkl"))
    metadata = json.loads(sidecar.read_text())
    stale = pd.read_pickle(cache)
    stale["records"] = 999
    stale.to_pickle(cache)
    metadata["cache_sha256"] = cached_build.sha256(cache)
    del metadata["audit"]["padded_trailing_type_rows"]
    sidecar.write_text(json.dumps(metadata))
    assert cached_build.load_sst_boundary(sources, "VT").records.tolist() == [1]
    next(cached_build.BOUNDARY_CACHE.glob("*.audit.json")).unlink()
    next(cached_build.BOUNDARY_CACHE.glob("*.pkl")).write_bytes(b"unaudited")
    assert cached_build.load_sst_boundary(sources, "VT").records.tolist() == [1]


def test_pickle_hash_mismatch_invalidates_cache(cached_build, tmp_path):
    sources = tmp_path / "sources"
    write_boundary(sources, [boundary_row()])
    cached_build.load_sst_boundary(sources, "VT")
    next(cached_build.BOUNDARY_CACHE.glob("*.pkl")).write_bytes(b"modified")
    assert cached_build.load_sst_boundary(sources, "VT").records.tolist() == [1]


def test_unrecoverable_csv_quotes_fail_with_source_and_line(cached_build, tmp_path):
    sources = tmp_path / "sources"
    path = write_boundary(sources, [boundary_row()])
    with path.open("a", encoding="latin-1") as stream:
        stream.write('"unterminated\n')
    with pytest.raises(ValueError, match=r"VTB2026Q4.csv: malformed CSV near line 2"):
        cached_build.load_sst_boundary(sources, "VT")
    assert not cached_build.BOUNDARY_CACHE.exists()


def test_no_usable_rows_does_not_write_cache(cached_build, tmp_path):
    sources = tmp_path / "sources"
    write_boundary(sources, [boundary_row()[:-2]])
    with pytest.raises(
        ValueError, match="no usable boundary records; 1 malformed rows skipped"
    ):
        cached_build.load_sst_boundary(sources, "VT")
    assert not cached_build.BOUNDARY_CACHE.exists()


def test_chunk_boundaries_preserve_all_counts(cached_build, tmp_path):
    sources = tmp_path / "sources"
    path = write_boundary(
        sources, [boundary_row(), boundary_row()[:-1], boundary_row()]
    )
    audit = {}
    chunks = list(cached_build.sst_boundary_chunks(path, audit, chunksize=2))
    assert [len(chunk) for chunk in chunks] == [2, 1]
    assert audit["accepted_rows"] == 3
    assert audit["skipped_rows"] == 0
    assert audit["padded_trailing_type_rows"] == 1
