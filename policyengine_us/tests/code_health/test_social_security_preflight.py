"""Stored-data audits must catch inputs that bypass benefit reform formulas."""

from hashlib import sha256

import pandas as pd
import pytest

from policyengine_us.tools.social_security_preflight import (
    COMPONENTS,
    preflight_social_security_dataset,
)


def make_dataset(
    tmp_path,
    *,
    person_extra=None,
    tax_unit_extra=None,
    source_style="legacy",
    year=2024,
    storage_format="table",
):
    person = {"person_id": [1], "age": [70]}
    for public_name in COMPONENTS:
        name = public_name if source_style == "legacy" else f"{public_name}_reported"
        person[name] = [1_200]
    person.update(person_extra or {})
    tax_unit = {"tax_unit_id": [1]}
    tax_unit.update(tax_unit_extra or {})
    path = tmp_path / "synthetic.h5"
    with pd.HDFStore(path, mode="w") as store:
        store.put("person", pd.DataFrame(person), format=storage_format)
        store.put(
            "household", pd.DataFrame({"household_id": [1]}), format=storage_format
        )
        store.put("tax_unit", pd.DataFrame(tax_unit), format=storage_format)
        store.put("_time_period", pd.Series([year]), format=storage_format)
    return path


def audit(path, **kwargs):
    return preflight_social_security_dataset(
        path,
        artifact="synthetic://social-security-preflight",
        expected_sha256=sha256(path.read_bytes()).hexdigest(),
        **kwargs,
    )


@pytest.mark.parametrize("storage_format", ["table", "fixed"])
def test_receipt_records_actual_stored_sources(tmp_path, storage_format):
    path = make_dataset(tmp_path, storage_format=storage_format)
    digest = sha256(path.read_bytes()).hexdigest()
    receipt = audit(path, intentional_final_overrides=["employment_income"])

    assert receipt["artifact"] == "synthetic://social-security-preflight"
    assert receipt["sha256"] == digest
    assert receipt["base_year"] == 2024
    assert receipt["stored_h5_keys"] == [
        "/_time_period",
        "/household",
        "/person",
        "/tax_unit",
    ]
    assert receipt["stored_column_count"] == 8
    assert receipt["stored_columns"] == sorted(
        ["person_id", "household_id", "tax_unit_id", "age", *COMPONENTS]
    )
    assert receipt["row_counts"] == {"person": 1, "household": 1, "tax_unit": 1}
    assert receipt["source_mapping"] == {
        public_name: f"{public_name}_reported" for public_name in COMPONENTS
    }
    assert receipt["intentional_final_overrides"] == ["employment_income"]
    assert receipt["projection"]["method"] == "extend_single_year_dataset"
    assert receipt["projection"]["end_year"] == 2035
    assert receipt["projection"]["carry_inferred_history_across_years"] is False
    assert sha256(path.read_bytes()).hexdigest() == digest


def test_reported_columns_are_not_migrated_again(tmp_path):
    receipt = audit(make_dataset(tmp_path, source_style="reported"))
    assert receipt["source_mapping"] == {
        f"{public_name}_reported": f"{public_name}_reported"
        for public_name in COMPONENTS
    }


@pytest.mark.parametrize(
    "column",
    [
        "social_security",
        "social_security_across_the_board_factor",
        "social_security_payable_factor",
        "social_security_retirement_base",
        "social_security_retirement_joint_cola_factor",
        "social_security_retirement_pia_ratio_factor",
        "social_security_dependents_payable_factor",
        "employee_social_security_tax",
        "employer_social_security_tax",
        "self_employment_social_security_tax",
        "employer_total_social_security_tax",
        "net_investment_income_tax",
        "niit_liability",
        "niit_revenue_oasdi",
        "oasdi_niit_revenue",
        "tob_revenue_oasdi",
        "tob_revenue_medicare_hi",
        "tob_revenue_total",
        "s770_revenue_oasdi",
        "s770_existing_niit_revenue_oasdi",
        "s770_nii_addon_tax",
        "s770_active_business_income_tax",
        "owners_draw_oasdi_tax",
        "oasdi_payroll_tax_revenue",
        "oasdi_benefit_taxation_revenue",
        "oasdi_income",
        "oasdi_cost",
        "oasdi_modeled_balance",
    ],
)
def test_stored_outputs_rejected_even_when_zero(tmp_path, column):
    path = make_dataset(tmp_path, tax_unit_extra={column: [0]})
    with pytest.raises(ValueError, match="bypass reform formulas"):
        audit(path)


@pytest.mark.parametrize(
    "entity, column",
    [
        ("person", "s770_passive_se_income"),
        ("person", "s770_active_fica_income"),
        ("tax_unit", "s770_nii_fica_seca_income"),
        ("tax_unit", "s770_niit_nol_deduction"),
        ("person", "s770_draw_gross"),
        ("person", "s770_draw_oasdi_base"),
        ("person", "s770_draw_hi_in_effect"),
        ("person", "owners_draw_subsets_are_disjoint"),
        ("person", "owners_draw_passive_se_overlap"),
    ],
)
def test_section_8_and_owners_draw_classification_inputs_remain_sources(
    tmp_path, entity, column
):
    path = make_dataset(tmp_path, **{f"{entity}_extra": {column: [0]}})
    assert column in audit(path)["stored_columns"]


def test_both_component_names_would_preserve_a_bypassing_override(tmp_path):
    path = make_dataset(
        tmp_path, person_extra={"social_security_retirement_reported": [0]}
    )
    with pytest.raises(ValueError, match="exactly one Person source"):
        audit(path)


def test_missing_component_cannot_be_invented_from_aggregate(tmp_path):
    path = make_dataset(tmp_path)
    with pd.HDFStore(path, mode="a") as store:
        person = store["person"].drop(columns=["social_security_disability"])
        store.put("person", person, format="table")
    with pytest.raises(ValueError, match="exactly one Person source"):
        audit(path)


@pytest.mark.parametrize(
    "name",
    [
        "social_security",
        "social_security_retirement",
        "tob_revenue_oasdi",
        "social_security_payable_factor",
    ],
)
def test_population_final_overrides_rejected(tmp_path, name):
    path = make_dataset(tmp_path)
    with pytest.raises(ValueError, match="cannot use final benefit or tax overrides"):
        audit(path, intentional_final_overrides=[name])


def test_hash_must_match_the_selected_artifact(tmp_path):
    path = make_dataset(tmp_path)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        preflight_social_security_dataset(
            path,
            artifact="synthetic://social-security-preflight",
            expected_sha256="0" * 64,
        )


def test_certified_identity_cannot_be_attached_to_alternative_bytes(tmp_path):
    path = make_dataset(tmp_path)
    with pytest.raises(ValueError, match="pins cannot be changed"):
        preflight_social_security_dataset(
            path, expected_sha256=sha256(path.read_bytes()).hexdigest()
        )


def test_base_year_comes_from_h5_not_the_filename(tmp_path):
    path = make_dataset(tmp_path, year=2023)
    with pytest.raises(ValueError, match="base year mismatch"):
        audit(path)


def test_base_year_must_be_stored(tmp_path):
    path = make_dataset(tmp_path)
    with pd.HDFStore(path, mode="a") as store:
        store.remove("_time_period")
    with pytest.raises(ValueError, match="must store its base year"):
        audit(path)


def test_columns_cannot_be_duplicated_across_entities(tmp_path):
    path = make_dataset(tmp_path, tax_unit_extra={"social_security_retirement": [0]})
    with pytest.raises(ValueError, match="Columns appear more than once"):
        audit(path)


def test_projection_horizon_must_include_base_year(tmp_path):
    path = make_dataset(tmp_path)
    with pytest.raises(ValueError, match="end year precedes"):
        audit(path, projection_end_year=2023)


def test_table_inventory_does_not_read_entity_rows(tmp_path, monkeypatch):
    path = make_dataset(tmp_path)
    original_select = pd.HDFStore.select

    def select_metadata_only(self, key, *args, **kwargs):
        assert key.strip("/") == "_time_period", "Entity rows must not be loaded."
        return original_select(self, key, *args, **kwargs)

    monkeypatch.setattr(pd.HDFStore, "select", select_metadata_only)
    assert audit(path)["stored_column_count"] == 8
