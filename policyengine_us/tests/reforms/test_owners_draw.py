"""Structural activation, isolation, and vector invariants for owners' draw.

Dollar examples live in owners_draw.yaml. These tests capture the installed
formula classes and run small deterministic vectors without copying model
trees. One integration test creates a reformed simulation against the shared
read-only baseline to exercise the public parameter-only activation route.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.periods import period
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.ssa.owners_draw import (
    create_owners_draw,
    create_owners_draw_reform,
)
from policyengine_us.system import system
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.self_employment_tax_ald_person import (
    self_employment_tax_ald_person,
)
from policyengine_us.variables.gov.irs.tax.payroll.social_security.taxable_earnings_for_social_security import (
    taxable_earnings_for_social_security,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_medicare_tax import (
    self_employment_medicare_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_social_security_tax import (
    self_employment_social_security_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_tax import (
    self_employment_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.social_security_taxable_self_employment_income import (
    social_security_taxable_self_employment_income,
)
from policyengine_us.variables.gov.irs.tax.self_employment.taxable_self_employment_income import (
    taxable_self_employment_income,
)


BASELINE_VARIABLES = {
    variable.__name__: variable
    for variable in (
        taxable_earnings_for_social_security,
        taxable_self_employment_income,
        social_security_taxable_self_employment_income,
        self_employment_social_security_tax,
        self_employment_medicare_tax,
        self_employment_tax,
        self_employment_tax_ald_person,
    )
}
PERIOD = period("2027")
CAP = 200_000


@pytest.fixture(scope="module")
def reform_variables():
    installed = []
    create_owners_draw().apply(SimpleNamespace(update_variable=installed.append))
    return BASELINE_VARIABLES | {
        variable.__name__: variable
        for variable in installed
        if variable.__name__ != "ss_aime"
    }


def _parameters(**overrides):
    draw = SimpleNamespace(
        in_effect=True,
        start_year=2027,
        phase_in_years=10,
        phase_in_share=1,
        material_participation_only=True,
        net_earnings_factor=0,
        include_hi=False,
        half_seca_deduction=True,
        benefit_credit=True,
        room_cap_basis=0,
        current_law_cap=CAP,
    )
    for name, value in overrides.items():
        setattr(draw, name, value)
    root = SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                ssa=SimpleNamespace(owners_draw=draw),
                ubi_center=SimpleNamespace(
                    flat_tax=SimpleNamespace(abolish_self_emp_tax=False)
                ),
            ),
            irs=SimpleNamespace(
                payroll=SimpleNamespace(social_security=SimpleNamespace(cap=CAP)),
                self_employment=SimpleNamespace(
                    rate=SimpleNamespace(social_security=0.124, medicare=0.029),
                    net_earnings_exemption=400,
                ),
                ald=SimpleNamespace(
                    misc=SimpleNamespace(employer_share=0.5),
                    self_employment_tax=SimpleNamespace(percent_deductible=0.5),
                ),
            ),
        )
    )
    return lambda instant: root


def _calculate(variables, parameters, inputs, outputs=None):
    values = {
        "s_corp_income": 0,
        "partnership_income": 0,
        "passive_partnership_s_corp_income": 0,
        "partnership_self_employment_net_earnings": 0,
        "owners_draw_subsets_are_disjoint": True,
        "owners_draw_passive_se_overlap": np.nan,
        "self_employment_income": 0,
        "sstb_self_employment_income": 0,
        "farm_operations_income": 0,
        "payroll_tax_gross_wages": 0,
        **inputs,
    }

    values = {name: np.asarray(value) for name, value in values.items()}

    def person(name, instant, options=None):
        if name not in values:
            values[name] = variables[name].formula(person, instant, parameters)
        return values[name]

    # Core's add() checks entity metadata before summing Person variables.
    person.entity = SimpleNamespace(is_person=True, key="person")
    person.entity.get_variable = lambda name: SimpleNamespace(entity=person.entity)

    for name in outputs or variables:
        if name not in (
            "owners_draw_subsets_are_disjoint",
            "owners_draw_passive_se_overlap",
        ):
            person(name, PERIOD)
    return values


VECTOR_INPUTS = {
    "payroll_tax_gross_wages": np.array(
        [0, 100_000, 200_000, 300_000, 0, 90_000, 199_999, 0], dtype=float
    ),
    "s_corp_income": np.array(
        [150_000, 200_000, 300_000, 150_000, -50_000, 100_000, 500_000, 433],
        dtype=float,
    ),
    "self_employment_income": np.array(
        [0, 50_000, 0, 50_000, 80_000, 100_000, 1_000, 0], dtype=float
    ),
    "partnership_income": np.array(
        [0, 30_000, 40_000, 0, 20_000, 20_000, 0, 0], dtype=float
    ),
    "partnership_self_employment_net_earnings": np.array(
        [0, 30_000, 0, 0, 0, 20_000, 0, 0], dtype=float
    ),
}


def test_vector_invariants_and_phase_monotonicity(reform_variables):
    prior_base = np.zeros(8)
    prior_tax = np.zeros(8)
    for share in (0, 0.1, 0.3, 0.7, 1):
        values = _calculate(
            reform_variables, _parameters(phase_in_share=share), VECTOR_INPUTS
        )
        base = values["owners_draw_oasdi_base"]
        gross = values["owners_draw_gross"]
        room = values["owners_draw_oasdi_room"]
        tax = values["owners_draw_oasdi_tax"]
        assert np.all(base >= 0)
        assert np.all(base <= room)
        assert np.all(base <= gross)
        assert np.all(base >= prior_base)
        assert np.all(tax >= prior_tax)
        total_earnings = (
            values["taxable_earnings_for_social_security"]
            + values["social_security_taxable_self_employment_income"]
            + base
        )
        assert np.all(total_earnings <= CAP)
        # M7 cannot exclude untaxed or undrawn profits from the active base.
        exclusion = values["owners_draw_niit_exclusion"]
        assert np.all(exclusion >= 0)
        assert np.all(exclusion <= gross + 1e-8)
        np.testing.assert_allclose(exclusion * 0.9235, base)
        prior_base, prior_tax = base, tax


def test_disabled_formulas_equal_baseline_on_the_same_vectors(reform_variables):
    parameters = _parameters(in_effect=False)
    baseline = _calculate(BASELINE_VARIABLES, parameters, VECTOR_INPUTS)
    reformed = _calculate(reform_variables, parameters, VECTOR_INPUTS)
    for name in BASELINE_VARIABLES:
        np.testing.assert_array_equal(reformed[name], baseline[name], err_msg=name)
    for name in reform_variables.keys() - BASELINE_VARIABLES.keys():
        if name not in (
            "owners_draw_subsets_are_disjoint",
            "owners_draw_passive_se_overlap",
        ):
            assert np.all(np.asarray(reformed[name]) == 0), name


def test_already_se_partnership_income_cannot_add_a_second_draw(reform_variables):
    already_se = np.array([0, 399, 1_000, 100_000, 500_000], dtype=float)
    inputs = {
        "partnership_income": already_se,
        "partnership_self_employment_net_earnings": already_se,
    }
    parameters = _parameters()
    baseline = _calculate(BASELINE_VARIABLES, parameters, inputs)
    reformed = _calculate(reform_variables, parameters, inputs)
    assert np.all(reformed["owners_draw_gross"] == 0)
    assert np.all(reformed["owners_draw_oasdi_base"] == 0)
    for name in BASELINE_VARIABLES:
        np.testing.assert_array_equal(reformed[name], baseline[name], err_msg=name)


@pytest.mark.parametrize(
    "inputs, message",
    [
        (
            {
                "owners_draw_subsets_are_disjoint": False,
                "owners_draw_passive_se_overlap": np.nan,
            },
            "validated disjoint",
        ),
        (
            {
                "owners_draw_subsets_are_disjoint": True,
                "owners_draw_passive_se_overlap": 1_000,
            },
            "contradicts",
        ),
    ],
)
def test_ambiguous_or_contradictory_classification_is_rejected(
    reform_variables, inputs, message
):
    with pytest.raises(ValueError, match=message):
        _calculate(
            reform_variables,
            _parameters(),
            {
                "partnership_income": np.array([100_000, 50_000]),
                "partnership_self_employment_net_earnings": np.array([40_000, 0]),
                "passive_partnership_s_corp_income": np.array([20_000, 0]),
                **inputs,
            },
            outputs=["owners_draw_active_income"],
        )


@pytest.mark.parametrize(
    "overrides, output, message",
    [
        ({"phase_in_years": 0}, "owners_draw_gross", "positive integer"),
        ({"phase_in_years": 1.5}, "owners_draw_gross", "positive integer"),
        ({"phase_in_share": 1.01}, "owners_draw_gross", "phase_in_share"),
        ({"phase_in_share": -0.1}, "owners_draw_gross", "phase_in_share"),
        ({"net_earnings_factor": 1.1}, "owners_draw_gross", "net earnings factor"),
        ({"net_earnings_factor": -0.1}, "owners_draw_gross", "net earnings factor"),
        ({"room_cap_basis": 2}, "owners_draw_oasdi_room", "room_cap_basis"),
    ],
)
def test_invalid_policy_settings_fail_explicitly(
    reform_variables, overrides, output, message
):
    with pytest.raises(ValueError, match=message):
        _calculate(
            reform_variables,
            _parameters(**overrides),
            {"s_corp_income": 100_000},
            outputs=[output],
        )


def test_future_parameter_activation_captures_cap_and_preserves_baseline():
    years = (2026, 2036, 2037)
    situation = {
        "people": {
            "owner": {
                "age": {year: 45 for year in years},
                "payroll_tax_gross_wages": {year: 150_000 for year in years},
                "self_employment_income": {year: 50_000 for year in years},
                "s_corp_income": {year: 400_000 for year in years},
            },
            "past_owner": {
                "age": {year: year - 1975 for year in years},
                "s_corp_income": {2026: 0, 2036: 150_000, 2037: 0},
            },
        }
    }
    parameter_reform = Reform.from_dict(
        {
            "gov.contrib.ssa.owners_draw.in_effect": {
                "2036-01-01.2036-12-31": True,
                "2037-01-01.2100-12-31": False,
            },
            "gov.irs.payroll.social_security.cap": {"2036-01-01.2100-12-31": np.inf},
            "gov.simulation.aime_lookback_years": {"2026-01-01.2100-12-31": 1},
        },
        country_id="us",
    )
    baseline = Simulation(tax_benefit_system=system, situation=situation)
    reformed = Simulation(
        tax_benefit_system=system, situation=situation, reform=parameter_reform
    )

    # Parameter-only activation must discover a finite active interval twelve
    # years beyond the default 2024 factory start, including its later end.
    assert create_owners_draw_reform(system.parameters, "2024-01-01") is None
    unaffected_outputs = (
        *BASELINE_VARIABLES,
        "irs_gross_income",
        "adjusted_gross_income",
        "niit_magi",
        "net_investment_income_tax",
        "income_tax",
    )
    for year in (2026, 2037):
        for name in unaffected_outputs:
            np.testing.assert_array_equal(
                reformed.calculate(name, year),
                baseline.calculate(name, year),
                err_msg=f"{name} in inactive {year}",
            )
        assert reformed.calculate("owners_draw_gross", year)[0] == 0

    cap = system.parameters("2036-01-01").gov.irs.payroll.social_security.cap
    reformed_parameters = reformed.tax_benefit_system.parameters("2036-01-01")
    assert np.isinf(reformed_parameters.gov.irs.payroll.social_security.cap)
    assert reformed_parameters.gov.contrib.ssa.owners_draw.current_law_cap == cap
    expected_room = max(0, cap - 150_000 - 46_175)
    assert reformed.calculate("owners_draw_oasdi_room", 2036)[0] == pytest.approx(
        expected_room
    )
    assert reformed.calculate("owners_draw_oasdi_base", 2036)[0] == pytest.approx(
        min(369_400, expected_room)
    )

    # Covered earnings retain the earning year's classification when the
    # calculation/payment year is inactive. The 62-year-old's sole draw was
    # earned at age 61, after the age-60 indexing year, so no wage indexing
    # applies: 138,525 / (35 * 12) = 329.8214286.
    assert reformed.calculate("owners_draw_credited_earnings", 2036)[
        1
    ] == pytest.approx(138_525)
    assert reformed.calculate("owners_draw_credited_earnings", 2037)[1] == 0
    assert reformed.calculate("ss_aime", 2037)[1] == pytest.approx(138_525 / 420)

    # Neither the captured current-law path nor the shared baseline was mutated
    # by removing the tax ceiling in the reformed simulation.
    assert system.parameters("2036-01-01").gov.irs.payroll.social_security.cap == cap
    assert not system.parameters("2036-01-01").gov.contrib.ssa.owners_draw.in_effect
