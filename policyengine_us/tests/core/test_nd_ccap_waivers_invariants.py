import numpy as np
import pytest
from hypothesis import example, given, settings, strategies as st

from policyengine_us import Simulation


CASE_COUNT = 12
WAIVER_INPUTS = (
    "nd_ccap_crossroads_enrolled",
    "nd_ccap_tanf_diversion_enrolled",
    "nd_ccap_arsen_enrolled",
)
CARETAKER_INPUTS = (
    "nd_ccap_has_disqualified_alien_caretaker",
    "nd_ccap_has_ineligible_non_legally_responsible_caretaker",
    "nd_ccap_has_ineligible_kinship_caretaker",
)


@pytest.fixture(scope="module")
def simulation():
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for index in range(CASE_COUNT):
        parent = f"parent_{index}"
        child = f"child_{index}"
        situation["people"][parent] = {}
        situation["people"][child] = {}
        members = [parent, child]
        for entity in ("tax_units", "spm_units", "families", "households"):
            situation[entity][f"unit_{index}"] = {"members": members}
        for person in members:
            situation["marital_units"][person] = {"members": [person]}
    return Simulation(situation=situation)


@settings(max_examples=8, deadline=None, derandomize=True)
@example(
    period="2026-10",
    income=4_500,
    monthly_smi=10_000,
    tanf=False,
    enrolled=False,
    child_ssi=True,
    caretakers=(False, False, False),
    tanf_eligible_child=False,
)
@example(
    period="2026-10",
    income=5_000,
    monthly_smi=10_000,
    tanf=True,
    enrolled=False,
    child_ssi=True,
    caretakers=(True, True, True),
    tanf_eligible_child=False,
)
@example(
    period="2026-09",
    income=50_000,
    monthly_smi=10_000,
    tanf=True,
    enrolled=True,
    child_ssi=True,
    caretakers=(False, False, True),
    tanf_eligible_child=True,
)
@example(
    period="2024-07",
    income=-1_000,
    monthly_smi=10_000,
    tanf=False,
    enrolled=False,
    child_ssi=False,
    caretakers=(False, False, False),
    tanf_eligible_child=False,
)
@given(
    period=st.sampled_from(("2024-07", "2025-10", "2026-09", "2026-10")),
    income=st.integers(min_value=-100_000, max_value=1_000_000_000),
    monthly_smi=st.integers(min_value=0, max_value=25_000),
    tanf=st.booleans(),
    enrolled=st.booleans(),
    child_ssi=st.booleans(),
    caretakers=st.tuples(st.booleans(), st.booleans(), st.booleans()),
    tanf_eligible_child=st.booleans(),
)
def test_nd_ccap_waivers_preserve_bounds_and_default_behavior(
    simulation,
    period,
    income,
    monthly_smi,
    tanf,
    enrolled,
    child_ssi,
    caretakers,
    tanf_eligible_child,
):
    year = period[:4]
    simulation.drop_computed_arrays()
    simulation.set_input("state_code", year, ["ND"] * CASE_COUNT)
    simulation.set_input("age", year, [30, 3] * CASE_COUNT)
    simulation.set_input("is_disabled", year, [False] * (2 * CASE_COUNT))
    # Every child attends care, so a child's SSI can trigger the exception.
    simulation.set_input("childcare_hours_per_week", year, [0, 40] * CASE_COUNT)
    simulation.set_input("hhs_smi", year, [monthly_smi * 12] * CASE_COUNT)
    simulation.set_input("nd_ccap_countable_income", period, [income] * CASE_COUNT)
    # Isolate the co-payment calculation from the other eligibility tests.
    simulation.set_input("nd_ccap_eligible", period, [True] * CASE_COUNT)
    simulation.set_input("is_tanf_enrolled", period, [tanf] * 10 + [True, True])
    simulation.set_input(
        "is_nd_ccap_enrolled",
        period,
        [enrolled] * 4 + [False, True] + [enrolled] * 6,
    )

    workforce = np.zeros(2 * CASE_COUNT, dtype=bool)
    workforce[[8, 10, 18]] = True
    simulation.set_input("nd_ccap_workforce_benefit_eligible_parent", period, workforce)
    for variable, waived_case in zip(WAIVER_INPUTS, (6, 7, 8)):
        values = np.zeros(CASE_COUNT, dtype=bool)
        values[[waived_case, 9]] = True
        simulation.set_input(variable, period, values)

    for variable, caretaker in zip(CARETAKER_INPUTS, caretakers):
        values = [False] * 3 + [caretaker] * 7 + [False, False]
        if variable == "nd_ccap_has_ineligible_kinship_caretaker":
            values[-2:] = [True, True]
        simulation.set_input(variable, period, values)
    simulation.set_input(
        "nd_ccap_has_tanf_eligible_child",
        period,
        [False] * 3 + [tanf_eligible_child] * 7 + [False, True],
    )

    ssi = np.zeros(2 * CASE_COUNT)
    ssi[3] = 1
    ssi[4] = 1
    for index in range(3, 10):
        ssi[2 * index + 1] = int(child_ssi)
    simulation.set_input("ssi", period, ssi)

    inputs = (
        "nd_ccap_workforce_benefit_eligible_parent",
        *WAIVER_INPUTS,
        *CARETAKER_INPUTS,
        "nd_ccap_has_tanf_eligible_child",
    )
    for variable in inputs:
        assert simulation.tax_benefit_system.variables[variable].default_value is False

    countable_income = simulation.calculate("nd_ccap_countable_income", period)
    smi = simulation.calculate("hhs_smi", period)
    positive_income = np.maximum(countable_income, 0)
    income_to_smi = np.divide(
        positive_income,
        smi,
        out=np.zeros_like(positive_income),
        where=smi > 0,
    )
    p = simulation.tax_benefit_system.parameters(period).gov.states.nd.dhs.ccap
    unwaived = np.minimum(
        p.copay.rate.calc(income_to_smi) * smi,
        p.copay.max_rate * positive_income,
    )
    copay = simulation.calculate("nd_ccap_copay", period)
    assert np.all(copay >= 0)
    assert np.all(copay <= unwaived + 0.01)
    np.testing.assert_allclose(copay[[4, 5, 6, 8, 9]], 0, atol=0.01)
    assert np.all(copay[4:10] <= copay[3] + 0.01)
    kinship_exception = caretakers[2] and not (
        period >= "2026-10" and tanf_eligible_child
    )
    diversion_exception = (
        caretakers[0]
        or caretakers[1]
        or kinship_exception
        or (period >= "2026-10" and child_ssi)
    )
    expected_diversion_copay = (
        unwaived[7]
        if diversion_exception and income_to_smi[7] > p.copay.waiver_smi_threshold
        else 0
    )
    np.testing.assert_allclose(copay[7], expected_diversion_copay, atol=0.01)
    assert copay[11] <= copay[10] + 0.01
    if period >= "2026-10":
        assert copay[11] == 0
    else:
        assert copay[11] == copay[10]

    # Preserve main's calculation, except that SSI can end the TANF waiver:
    # a caretaker's SSI (unit 2) before October 2026, and a child's SSI
    # (unit 1) from then on.
    expected = np.where(
        (income_to_smi[:3] <= p.copay.waiver_smi_threshold) | tanf,
        0,
        unwaived[:3],
    )
    ssi_exception = 1 if period >= "2026-10" else 2
    if tanf:
        expected[ssi_exception] = (
            0
            if income_to_smi[ssi_exception] <= p.copay.waiver_smi_threshold
            else unwaived[ssi_exception]
        )
    np.testing.assert_allclose(copay[:3], expected, atol=0.01)

    income_eligible = simulation.calculate("nd_ccap_income_eligible", period)
    rate = p.income.continuing_smi_rate if enrolled else p.income.initial_smi_rate
    np.testing.assert_array_equal(
        income_eligible[:3], countable_income[:3] <= smi[:3] * rate
    )
    assert np.all(income_eligible[4:6])

    # Units 4, 5 and 9 have a Workforce Benefit caretaker and no other modeled
    # activity. North Dakota waives the second caretaker's activity test
    # through December 2025 (ML 3819) and restores it in January 2026.
    activity = simulation.calculate("nd_ccap_activity_eligible", period)
    if period < "2026-01":
        assert np.all(activity[[4, 5, 9]])
    else:
        np.testing.assert_array_equal(activity[[4, 5, 9]], activity[[0, 0, 0]])
