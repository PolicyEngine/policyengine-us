import pytest

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.data import (
    dataset_input_metadata,
    dataset_input_variables,
    get_dataset_input_metadata,
    is_dataset_exportable_variable,
    is_dataset_input_variable,
    is_formula_owned_variable,
)


def test_dataset_input_contract_marks_stochastic_status_inputs():
    expected = {
        "takes_up_aca_if_eligible",
        "takes_up_dc_ptc",
        "takes_up_eitc",
        "takes_up_head_start_if_eligible",
        "takes_up_early_head_start_if_eligible",
        "takes_up_medicaid_if_eligible",
        "takes_up_snap_if_eligible",
        "takes_up_tanf_if_eligible",
        "would_claim_wic",
    }

    assert expected <= dataset_input_variables(kind="stochastic_status")


def test_dataset_input_contract_marks_known_formula_overrides():
    system = CountryTaxBenefitSystem()

    for variable in ("has_tin", "has_itin", "in_nyc", "fsla_overtime_premium"):
        assert is_dataset_input_variable(variable)
        assert is_dataset_exportable_variable(variable, system=system)
        assert not is_formula_owned_variable(variable, system=system)


def test_dataset_input_contract_marks_medical_inputs():
    metadata = get_dataset_input_metadata("meets_ssi_disability_criteria")

    assert metadata is not None
    assert metadata.kind == "medical_status"
    assert "SSI" in metadata.rationale
    assert "is_wic_at_nutritional_risk" in dataset_input_variables(
        kind="medical_status"
    )


def test_formula_owned_helper_rejects_computed_outputs():
    system = CountryTaxBenefitSystem()

    assert is_formula_owned_variable("wic", system=system)
    assert not is_dataset_exportable_variable("wic", system=system)


def test_dataset_input_contract_is_consistent_with_model_variables():
    system = CountryTaxBenefitSystem()
    metadata = dataset_input_metadata()

    missing = sorted(set(metadata) - set(system.variables))
    assert missing == []

    undocumented_defaults = {
        name
        for name, variable in system.variables.items()
        if name.startswith(("takes_up_", "would_claim_"))
        and getattr(variable, "default_value", None) is True
        and name not in metadata
    }
    assert undocumented_defaults == set()


def test_dataset_contract_helpers_raise_for_unknown_variables():
    with pytest.raises(KeyError):
        is_formula_owned_variable("not_a_variable")

    with pytest.raises(KeyError):
        is_dataset_exportable_variable("not_a_variable")
