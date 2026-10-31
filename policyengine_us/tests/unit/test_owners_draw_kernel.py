"""Pure-kernel extraction differential, including public intermediate inputs.

The independent reference freezes arithmetic from the merged reform before the
extraction. It avoids model construction and tests the compatibility contract
that annual history and installed Variables must share.
"""

from dataclasses import fields, replace
import gc
from types import SimpleNamespace
import weakref

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period

from policyengine_us.reforms.ssa.owners_draw import create_owners_draw
from policyengine_us.tools.social_security.owners_draw import (
    OwnersDrawInputs,
    OwnersDrawParameters,
    OwnersDrawResult,
    compute_owners_draw,
)


OUTPUTS = tuple(field.name for field in fields(OwnersDrawResult))
INPUTS = OwnersDrawInputs(
    s_corp_income=np.array([-50_000, 433, 434, 60_000, 150_000, 400_000]),
    partnership_income=np.array([20_000, 0, 0, 40_000, 100_000, 40_000]),
    passive_income=np.array([0, 0, 0, -20_000, 40_000, 20_000]),
    already_se_income=np.array([0, 0, 0, 30_000, 50_000, 40_000]),
    subsets_are_disjoint=np.array([True, True, True, True, False, False]),
    passive_se_overlap=np.array([np.nan, np.nan, np.nan, np.nan, 10_000, 20_000]),
    covered_wages=np.array([0, 0, 0, 30_000, 180_000, 250_000]),
    existing_covered_se=np.array([50_000, 0, 0, 20_000, 15_000, 0]),
)
PARAMETERS = OwnersDrawParameters(
    in_effect=True, phase_in_share=1, current_law_cap=200_000
)


@pytest.mark.parametrize(
    "output, override_intermediates",
    [("active_income", False), ("oasdi_base", True), (None, False)],
)
def test_returned_result_does_not_retain_person_accessors_until_cyclic_gc(
    output, override_intermediates
):
    class AccessorOwner:
        """A Person accessor also owns its simulation and policy in Core."""

        def __init__(self):
            self.annual = OwnersDrawInputs(s_corp_income=1_000)

        def annual_input(self, name):
            return getattr(self.annual, name)

        def intermediate(self, name):
            return {"net_earnings": 923.5, "oasdi_room": 200_000}[name]

    owner = AccessorOwner()
    observed = weakref.ref(owner)
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        result = compute_owners_draw(
            2027,
            inputs=owner.annual_input,
            parameters=PARAMETERS,
            output=output,
            overrides=owner.intermediate if override_intermediates else None,
        )
        del owner
        # No explicit collection: ordinary return must release both kinds of
        # callbacks even while callers keep the complete annual result alive.
        assert observed() is None
        assert (result.credited_earnings if output is None else result) == (
            1_000 if output == "active_income" else 923.5
        )
    finally:
        if was_enabled:
            gc.enable()


def _old_formula(output, year, inputs, p, overrides=None):
    """Arithmetic of the old Variables, independent of the extracted kernel."""
    values = dict(overrides or {})
    enabled = p.in_effect and year >= p.start_year

    def value(name):
        if name not in values:
            values[name] = formula(name)
        return values[name]

    def formula(name):
        if name == "active_income":
            if not enabled:
                return 0
            total = inputs.s_corp_income + inputs.partnership_income
            if not p.material_participation_only:
                return total - inputs.already_se_income
            overlap = np.where(
                np.isfinite(inputs.passive_se_overlap), inputs.passive_se_overlap, 0
            )
            return total - inputs.passive_income - inputs.already_se_income + overlap
        if name == "phase_in_share":
            if not enabled:
                return 0
            return (
                min(1, (year - p.start_year + 1) / p.phase_in_years)
                if p.phase_in_share == -1
                else p.phase_in_share
            )
        if name == "planned_gross":
            return formula("phase_in_share") * np.maximum(0, value("active_income"))
        if name == "net_earnings_factor":
            if not enabled:
                return 0
            return p.net_earnings_factor or (
                1 - p.employer_share * (p.oasdi_rate + p.hi_rate)
            )
        if name == "gross":
            if not enabled:
                return 0
            planned = value("planned_gross")
            adjusted = planned * value("net_earnings_factor")
            return np.where(adjusted >= p.reporting_floor, planned, 0)
        if name == "net_earnings":
            return value("gross") * value("net_earnings_factor")
        if name == "oasdi_room":
            if not enabled:
                return 0
            if p.room_cap_basis == 1:
                return np.inf
            return np.maximum(
                0, p.current_law_cap - inputs.covered_wages - inputs.existing_covered_se
            )
        if name == "oasdi_base":
            return np.minimum(value("net_earnings"), value("oasdi_room"))
        if name == "oasdi_tax":
            return p.oasdi_rate * value("oasdi_base")
        if name == "hi_tax":
            return p.hi_rate * value("net_earnings") if p.include_hi else 0
        if name == "niit_exclusion":
            if not enabled:
                return 0
            if p.include_hi:
                return value("gross")
            return value("oasdi_base") / value("net_earnings_factor")
        if name == "credited_earnings":
            return value("net_earnings") if p.benefit_credit else 0
        raise AssertionError(name)

    # A supplied target would bypass its Variable; overrides apply only to
    # dependencies when invoking a formula directly.
    return formula(output)


@pytest.mark.parametrize(
    "year, changes",
    [
        (2026, {}),
        (2027, {}),
        (2029, {"phase_in_share": -1}),
        (2036, {"phase_in_share": -1}),
        (2054, {"phase_in_share": -1}),
        (2027, {"in_effect": False}),
        (2027, {"phase_in_share": 0}),
        (2027, {"material_participation_only": False}),
        (2027, {"net_earnings_factor": 0.91}),
        (2027, {"oasdi_rate": 0.2, "hi_rate": 0.04, "employer_share": 0.4}),
        (2027, {"reporting_floor": 1_000}),
        (2027, {"room_cap_basis": 1}),
        (2027, {"benefit_credit": False}),
        (2027, {"include_hi": True}),
        (2027, {"include_hi": True, "room_cap_basis": 1}),
    ],
)
def test_all_annual_outputs_equal_pre_extraction_formulas(year, changes):
    p = replace(PARAMETERS, **changes)
    result = compute_owners_draw(year, inputs=INPUTS, parameters=p)
    for output in OUTPUTS:
        np.testing.assert_array_equal(
            getattr(result, output),
            _old_formula(output, year, INPUTS, p),
            err_msg=output,
        )


@pytest.mark.parametrize(
    "output, overrides, changes",
    [
        ("planned_gross", {"active_income": np.array([-1, 10_000])}, {}),
        ("gross", {"planned_gross": np.array([400, 500])}, {}),
        ("gross", {"net_earnings_factor": 0.8}, {"net_earnings_factor": -1}),
        ("gross", {"planned_gross": 500}, {"phase_in_years": 0}),
        ("net_earnings", {"gross": 1_000}, {}),
        (
            "net_earnings",
            {"gross": 1_000, "net_earnings_factor": 0.8},
            {"in_effect": False},
        ),
        ("oasdi_base", {"net_earnings": 5_000}, {}),
        ("oasdi_base", {"oasdi_room": 123}, {"room_cap_basis": 2}),
        ("oasdi_tax", {"oasdi_base": 2_000}, {}),
        ("hi_tax", {"net_earnings": 2_000}, {"include_hi": True}),
        ("credited_earnings", {"net_earnings": 2_000}, {"in_effect": False}),
        ("credited_earnings", {"net_earnings": 2_000}, {"benefit_credit": False}),
        ("niit_exclusion", {"oasdi_base": 100, "net_earnings_factor": 0.8}, {}),
        ("niit_exclusion", {"gross": 123}, {"include_hi": True}),
    ],
)
def test_intermediate_overrides_equal_pre_extraction_formulas(
    output, overrides, changes
):
    p = replace(PARAMETERS, **changes)
    actual = compute_owners_draw(
        2027, inputs=INPUTS, parameters=p, output=output, overrides=overrides
    )
    np.testing.assert_array_equal(
        actual, _old_formula(output, 2027, INPUTS, p, overrides)
    )


def _policy_parameters(p):
    draw = SimpleNamespace(
        **{
            name: getattr(p, name)
            for name in (
                "in_effect",
                "start_year",
                "phase_in_years",
                "phase_in_share",
                "material_participation_only",
                "net_earnings_factor",
                "current_law_cap",
                "room_cap_basis",
                "include_hi",
                "benefit_credit",
            )
        }
    )
    gov = SimpleNamespace(
        contrib=SimpleNamespace(ssa=SimpleNamespace(owners_draw=draw)),
        irs=SimpleNamespace(
            ald=SimpleNamespace(misc=SimpleNamespace(employer_share=p.employer_share)),
            self_employment=SimpleNamespace(
                rate=SimpleNamespace(social_security=p.oasdi_rate, medicare=p.hi_rate),
                net_earnings_exemption=p.reporting_floor,
            ),
        ),
    )
    return lambda instant: SimpleNamespace(gov=gov)


def test_installed_formulas_delegate_to_the_same_kernel_and_honor_inputs():
    installed = []
    create_owners_draw().apply(SimpleNamespace(update_variable=installed.append))
    variables = {variable.__name__: variable for variable in installed}
    annual_period = period("2027")
    parameters = _policy_parameters(PARAMETERS)
    values = {
        "s_corp_income": INPUTS.s_corp_income,
        "partnership_income": INPUTS.partnership_income,
        "passive_partnership_s_corp_income": INPUTS.passive_income,
        "partnership_self_employment_net_earnings": INPUTS.already_se_income,
        "owners_draw_subsets_are_disjoint": INPUTS.subsets_are_disjoint,
        "owners_draw_passive_se_overlap": INPUTS.passive_se_overlap,
        "taxable_earnings_for_social_security": INPUTS.covered_wages,
        "social_security_taxable_self_employment_income": INPUTS.existing_covered_se,
        # Explicit public intermediate inputs must remain authoritative.
        "owners_draw_net_earnings_factor": 0.8,
        "owners_draw_oasdi_room": np.array([0, 1, 2, 3, 4, 5]),
    }

    def person(name, instant):
        if name not in values:
            values[name] = variables[name].formula(person, instant, parameters)
        return values[name]

    overrides = {
        "net_earnings_factor": values["owners_draw_net_earnings_factor"],
        "oasdi_room": values["owners_draw_oasdi_room"],
    }
    for output in OUTPUTS:
        if output == "phase_in_share" or output in overrides:
            continue
        np.testing.assert_array_equal(
            person(f"owners_draw_{output}", annual_period),
            _old_formula(output, 2027, INPUTS, PARAMETERS, overrides),
            err_msg=output,
        )


@pytest.mark.parametrize(
    "output",
    [
        "active_income",
        "planned_gross",
        "net_earnings_factor",
        "gross",
        "oasdi_room",
        "niit_exclusion",
    ],
)
def test_disabled_stages_do_not_read_unused_historical_policy_parameters(output):
    # Original disabled formulas return before consulting rates, caps, subset
    # inputs, or the reporting floor. Such parameters can be absent historically.
    gov = SimpleNamespace(
        contrib=SimpleNamespace(
            ssa=SimpleNamespace(
                owners_draw=SimpleNamespace(in_effect=False, start_year=2027)
            )
        )
    )
    p = OwnersDrawParameters.from_policy_parameters(gov, year=1983, output=output)
    overrides = {"active_income": 1_000}
    assert (
        compute_owners_draw(1983, parameters=p, output=output, overrides=overrides) == 0
    )


@pytest.mark.parametrize("include_hi", [False, True])
def test_m7_excludes_only_gross_profits_whose_net_earnings_face_seca(include_hi):
    result = compute_owners_draw(
        2027,
        inputs=OwnersDrawInputs(s_corp_income=100_000, covered_wages=190_000),
        parameters=replace(PARAMETERS, include_hi=include_hi),
    )
    assert result.net_earnings == 92_350
    assert result.oasdi_base == 10_000
    assert result.niit_exclusion == pytest.approx(
        100_000 if include_hi else 10_000 / 0.9235
    )
    # Credit follows the uncapped earnings ledger independently of tax room.
    assert result.credited_earnings == 92_350


@pytest.mark.parametrize(
    "inputs, message",
    [
        (
            OwnersDrawInputs(
                partnership_income=100, passive_income=20, already_se_income=10
            ),
            "validated disjoint",
        ),
        (
            OwnersDrawInputs(subsets_are_disjoint=True, passive_se_overlap=1),
            "contradicts",
        ),
    ],
)
def test_invalid_subset_assertions_keep_existing_failures(inputs, message):
    with pytest.raises(ValueError, match=message):
        compute_owners_draw(2027, inputs=inputs, parameters=PARAMETERS)


@given(
    total=st.floats(min_value=-1_000_000, max_value=1_000_000, allow_nan=False),
    wages=st.floats(min_value=0, max_value=1_000_000, allow_nan=False),
    existing_se=st.floats(min_value=0, max_value=200_000, allow_nan=False),
    share=st.floats(min_value=0, max_value=1, allow_nan=False),
)
@settings(max_examples=80, deadline=None)
def test_credit_is_the_single_adjusted_residual_before_tax_cap(
    total, wages, existing_se, share
):
    result = compute_owners_draw(
        2027,
        inputs=OwnersDrawInputs(
            s_corp_income=total, covered_wages=wages, existing_covered_se=existing_se
        ),
        parameters=replace(PARAMETERS, phase_in_share=share),
    )
    assert 0 <= result.credited_earnings <= max(total, 0)
    assert result.credited_earnings == result.net_earnings
    assert 0 <= result.oasdi_base <= result.net_earnings
    assert result.oasdi_base <= max(0, 200_000 - wages - existing_se)
