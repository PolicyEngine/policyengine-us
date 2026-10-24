"""Capture invented all-INCLUDED results in separately pinned model processes.

This file has no model imports at collection. A guarded runner explicitly opts
in with SPM_PARITY_VARIANT, SPM_PARITY_COUNTRY_ROOT and
SPM_PARITY_FORECAST_SHA256. It runs this exact file against baseline and port
environments separately; no country module or source overlay is permitted.
The comparison node reads only the two resulting, externally admitted JSON files.
"""

import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import re

import pytest


YEAR = 2024
STATUS = "spm_unit_spm_universe_status"
DEPENDENCIES = {
    "policyengine-core": "3.32.5",
    "microdf-python": "1.3.0",
    "spm-calculator": "1.0.0",
    "numpy": "2.4.6",
    "pandas": "3.0.3",
}
NULLABLE_INDICATORS = (
    "spm_unit_is_in_spm_poverty",
    "spm_unit_is_in_deep_spm_poverty",
    "in_poverty",
    "in_deep_poverty",
    "person_in_poverty",
)
VARIABLES = (
    "spm_unit_reference_spm_threshold",
    "spm_unit_unadjusted_spm_threshold",
    "spm_unit_spm_threshold",
    "spm_unit_spm_threshold_housing_portion",
    "spm_unit_geographic_adjustment",
    "spm_unit_capped_housing_subsidy",
    "spm_unit_benefits",
    "spm_unit_net_income",
    "poverty_line",
    "deep_poverty_line",
    "poverty_gap",
    "deep_poverty_gap",
    "spm_unit_oecd_equiv_net_income",
    "spm_unit_income_decile",
    *NULLABLE_INDICATORS,
    "housing_assistance",
    "spm_unit_allocated_housing_subsidy",
    "spm_unit_allocated_tenant_payment",
    "household_benefits",
    "household_net_income",
    "cbo_household_means_tested_transfers",
)


def _fixture_tables():
    """Four people, three SPM units and two households; no stored SPM outputs."""
    return {
        "person": {
            "person_id": [101, 102, 103, 201],
            "age": [40, 8, 17, 50],
            "employment_income": [6_000.0, 0.0, 10_000.0, 100_000.0],
            "is_spm_independent_minor_role": [False, False, True, False],
            "is_household_head": [True, False, False, True],
            "is_tax_unit_head": [True, False, True, True],
            "is_tax_unit_dependent": [False, True, False, False],
            "person_household_id": [10, 10, 10, 20],
            "person_spm_unit_id": [10, 10, 30, 20],
            "person_tax_unit_id": [10, 10, 30, 20],
            "person_family_id": [10, 10, 30, 20],
            "person_marital_unit_id": [101, 102, 103, 201],
        },
        "household": {
            "household_id": [10, 20],
            "household_weight": [2.0, 5.0],
            "state_code": ["CA", "NY"],
            "county_fips": ["06037", "36061"],
        },
        "spm_unit": {
            "spm_unit_id": [10, 30, 20],
            "spm_unit_tenure_type": ["RENTER", "RENTER", "RENTER"],
            "is_eligible_for_housing_assistance": [True, True, False],
            "takes_up_housing_assistance_if_eligible": [True, True, False],
            "hud_hap": [9_000.0, 0.0, 0.0],
            # The unawarded minor's hypothetical TTP must not be allocated.
            "hud_ttp": [900.0, 2_000.0, 0.0],
        },
        "tax_unit": {"tax_unit_id": [10, 30, 20]},
        "family": {"family_id": [10, 30, 20]},
        "marital_unit": {"marital_unit_id": [101, 102, 103, 201]},
    }


def _json_digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _compact_provenance(provenance):
    """Authenticate large forecast receipts without repeating bundled tables."""
    small_fields = {
        "forecast_id",
        "forecast_sha256",
        "scenario",
        "geography_kind",
        "runtime_versions",
        "composition_method",
        "storage_method",
    }
    assert set(provenance) == small_fields | {"years", "geographies"}
    return {
        **{key: provenance[key] for key in sorted(small_fields)},
        "full_sha256": _json_digest(provenance),
        "year_count": len(provenance["years"]),
        "years": {
            year: _json_digest(value) for year, value in provenance["years"].items()
        },
        "geographies": {
            "count": len(provenance["geographies"]),
            "sha256": _json_digest(provenance["geographies"]),
        },
    }


def _finite_number(value):
    result = float(value)
    assert math.isfinite(result), "All-INCLUDED fixture returned a nonfinite value"
    return result


def _values_by_id(simulation, variable, entity):
    ids = simulation.calc(f"{entity}_id", period=YEAR, map_to=entity)
    values = simulation.calc(variable, period=YEAR, map_to=entity)
    assert len(ids) == len(values)
    result = {
        str(int(ids.iloc[index])): _finite_number(values.iloc[index])
        for index in range(len(ids))
    }
    assert len(result) == len(ids), "Duplicate entity identity"
    return result


@pytest.mark.parametrize("geography", ["county", "national"])
def test_all_included_production_capture(geography):
    variant = os.environ.get("SPM_PARITY_VARIANT")
    if variant is None:
        pytest.skip("Explicit separately pinned parity process required")
    assert variant in {"baseline", "port"}
    country_root = Path(os.environ["SPM_PARITY_COUNTRY_ROOT"]).resolve(strict=True)
    forecast_sha = os.environ["SPM_PARITY_FORECAST_SHA256"]
    assert re.fullmatch(r"[a-f0-9]{64}", forecast_sha)
    artifact = Path(os.environ["BOUNDED_ARTIFACT_DIR"]).resolve(strict=True)
    assert artifact.is_dir()

    # The caller's guard and exact origin checks must already be active here.
    import pandas as pd
    import policyengine_us
    from policyengine_us import Microsimulation
    from policyengine_us.data.dataset_schema import USSingleYearDataset

    assert Path(policyengine_us.__file__).resolve() == (
        country_root / "policyengine_us/__init__.py"
    )
    versions = {name: metadata.version(name) for name in DEPENDENCIES}
    assert versions == DEPENDENCIES
    country_version = metadata.version("policyengine-us")
    assert (
        country_version
        == {
            "baseline": "2.2.1",
            "port": "2.2.1+spmuniverse.20260919",
        }[variant]
    )

    primitive_tables = _fixture_tables()
    primitive_sha = _json_digest(primitive_tables)
    tables = {name: pd.DataFrame(data) for name, data in primitive_tables.items()}
    if variant == "port":
        tables["spm_unit"][STATUS] = "INCLUDED"
    source = USSingleYearDataset(**tables, time_period=YEAR)
    source_before = [table.copy(deep=True) for table in source.tables]
    config = {
        "forecast_content_sha256": forecast_sha,
        "scenario": "ce_trend",
        "geography_kind": geography,
        "geography_id": None,
        "county_vintage": "2020",
        "as_of": "2026-09-09",
    }
    simulation = Microsimulation(dataset=source, spm=config)
    assert simulation.spm_config == config
    assert (STATUS in simulation.tax_benefit_system.variables) == (variant == "port")
    if variant == "port":
        assert list(simulation.calc(STATUS, period=YEAR)) == ["INCLUDED"] * 3

    # Check both nonzero allocation and an unassisted recipient's phantom TTP.
    assert _values_by_id(simulation, "housing_assistance", "spm_unit") == {
        "10": 9_000.0,
        "30": 0.0,
        "20": 0.0,
    }
    subsidy = _values_by_id(
        simulation, "spm_unit_allocated_housing_subsidy", "spm_unit"
    )
    assert subsidy == {
        "10": 6_000.0,
        "30": 3_000.0,
        "20": 0.0,
    }
    tenant_payment = _values_by_id(
        simulation, "spm_unit_allocated_tenant_payment", "spm_unit"
    )
    assert tenant_payment == {
        "10": 600.0,
        "30": 300.0,
        "20": 0.0,
    }
    caps = simulation.calc("spm_unit_capped_housing_subsidy", period=YEAR)
    assert (caps > 0).any(), "A zero-only fixture cannot qualify housing allocation"

    measures = {}
    for name in VARIABLES:
        entity = simulation.tax_benefit_system.variables[name].entity.key
        values = simulation.calc(name, period=YEAR, map_to="person")
        assert not values.isna().any(), name
        assert values.count() == 11, name  # Three people at weight2, one at weight5.
        if name in NULLABLE_INDICATORS:
            assert values.isin([0, 1]).all(), name
        measures[name] = {
            "entity": entity,
            "person_dtype": str(values.dtype),
            "entity_values": _values_by_id(simulation, name, entity),
            "person_values": _values_by_id(simulation, name, "person"),
            "weighted_count": _finite_number(values.count()),
            "weighted_sum": _finite_number(values.sum()),
            "weighted_mean": _finite_number(values.mean()),
        }
    for before, after in zip(source_before, source.tables, strict=True):
        pd.testing.assert_frame_equal(before, after)
    assert _json_digest(primitive_tables) == primitive_sha
    provenance = simulation.spm_provenance()
    assert set(provenance["years"]) == {str(YEAR)}
    record = {
        "schema": "spm-invented-production-parity/v2",
        "variant": variant,
        "country_root": str(country_root),
        "country_version": country_version,
        "dependency_versions": versions,
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "primitive_tables_sha256": primitive_sha,
        "year": YEAR,
        "spm_config": config,
        "measures": measures,
        "spm_provenance": _compact_provenance(provenance),
        "scope": "Invented all-INCLUDED fixture; no native or release qualification",
    }
    encoded = (
        json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode()
    assert len(encoded) < 128 * 1024
    with (artifact / f"spm-parity-{variant}-{geography}.json").open("xb") as stream:
        stream.write(encoded)


@pytest.mark.parametrize("geography", ["county", "national"])
def test_compare_all_included_production_captures(geography):
    if "SPM_PARITY_BASELINE_ARTIFACT_DIR" not in os.environ:
        pytest.skip("Two completed, separately admitted capture artifacts required")
    records = {}
    for variant in ("baseline", "port"):
        directory = Path(os.environ[f"SPM_PARITY_{variant.upper()}_ARTIFACT_DIR"])
        path = directory / f"spm-parity-{variant}-{geography}.json"
        assert path.stat().st_size < 128 * 1024
        record = json.loads(path.read_text())
        assert record["schema"] == "spm-invented-production-parity/v2"
        assert record["variant"] == variant
        assert (
            record["helper_sha256"]
            == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        )
        assert set(record["measures"]) == set(VARIABLES)
        assert record["dependency_versions"] == DEPENDENCIES
        assert record["year"] == YEAR
        provenance = record["spm_provenance"]
        assert provenance["runtime_versions"] == {
            "policyengine": None,
            "policyengine-us": record["country_version"],
            "policyengine-core": DEPENDENCIES["policyengine-core"],
            "spm-calculator": DEPENDENCIES["spm-calculator"],
        }
        assert provenance["year_count"] == 1
        assert set(provenance["years"]) == {str(YEAR)}
        assert (
            provenance["forecast_sha256"]
            == record["spm_config"]["forecast_content_sha256"]
        )
        records[variant] = record
    baseline, port = records["baseline"], records["port"]
    assert baseline["primitive_tables_sha256"] == port["primitive_tables_sha256"]
    assert baseline["spm_config"] == port["spm_config"]
    assert baseline["spm_config"]["geography_kind"] == geography
    assert baseline["country_root"] != port["country_root"]
    for key in baseline["spm_provenance"]:
        if key not in {"full_sha256", "runtime_versions"}:
            assert baseline["spm_provenance"][key] == port["spm_provenance"][key], key
    for name in VARIABLES:
        expected, actual = baseline["measures"][name], port["measures"][name]
        assert set(expected) == set(actual)
        for key in expected:
            if key == "person_dtype" and name in (
                *NULLABLE_INDICATORS,
                "spm_unit_income_decile",
            ):
                assert actual[key].startswith("float"), name
                continue
            assert actual[key] == expected[key], (name, key)
