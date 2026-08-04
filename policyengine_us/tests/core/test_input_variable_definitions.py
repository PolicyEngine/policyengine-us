from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.model_api import STATES


def _is_geographic_defined_for(defined_for: str) -> bool:
    return defined_for in STATES or defined_for.startswith("in_")


def _state_prefix(name):
    for state in STATES:
        if name.startswith(f"{state.lower()}_"):
            return state
    return None


def test_input_variables_do_not_use_non_geographic_defined_for():
    system = CountryTaxBenefitSystem()

    invalid = {
        name: variable.defined_for
        for name, variable in system.variables.items()
        if variable.is_input_variable()
        and variable.defined_for is not None
        and not _is_geographic_defined_for(variable.defined_for)
    }

    assert invalid == {}


def test_input_variables_do_not_use_formulas_adds_or_subtracts():
    system = CountryTaxBenefitSystem()

    invalid = {
        name: {
            "formulas": bool(getattr(variable, "formulas", None)),
            "adds": bool(getattr(variable, "adds", None)),
            "subtracts": bool(getattr(variable, "subtracts", None)),
        }
        for name, variable in system.variables.items()
        if variable.is_input_variable()
        and (
            getattr(variable, "formulas", None)
            or getattr(variable, "adds", None)
            or getattr(variable, "subtracts", None)
        )
    }

    assert invalid == {}


def test_legacy_marketplace_coverage_is_not_active_input_variable():
    system = CountryTaxBenefitSystem()

    legacy_variable = system.variables["has_marketplace_health_coverage"]
    assert not legacy_variable.is_input_variable()
    assert legacy_variable.formulas
    assert system.variables[
        "has_marketplace_health_coverage_at_interview"
    ].is_input_variable()
    assert system.variables["takes_up_aca_if_eligible"].is_input_variable()


def test_state_input_variables_match_state_defined_for():
    system = CountryTaxBenefitSystem()

    invalid = {
        name: variable.defined_for
        for name, variable in system.variables.items()
        if variable.is_input_variable()
        and _state_prefix(name) is not None
        and variable.defined_for in STATES
        and variable.defined_for != _state_prefix(name)
    }

    assert invalid == {}
