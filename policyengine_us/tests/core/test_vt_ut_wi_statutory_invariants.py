"""Invariants of four Vermont, Utah and Wisconsin rules.

1. Vermont student loan interest (32 V.S.A. 5811(21)(B)(vi), (29); IN-112
   line 16): from 2022, the state subtraction plus the federal deduction equals
   the filers' interest paid when AGI is within the limit, and the subtraction
   is zero above the limit, in 2021, and never negative.
2. Vermont child tax credit (5830f(b)): the phase-out applies per child, so the
   credit for n young children is n times the credit for one at the same AGI.
3. Utah at-home parent credit (59-10-1005(2)): a second spouse who also
   qualifies as an at-home parent does not change the credit.
4. Wisconsin homestead eligibility: the same under either head/spouse
   labelling, and marking a spouse as claimed never makes a return eligible.

Each check is one vectorized simulation over Hypothesis-drawn households.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

SETTINGS = settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _situation(units, year, state):
    """units: list of lists of person dicts; the first person is the head,
    the second (if flagged) the spouse, the rest dependents."""
    people, groups = (
        {},
        {
            k: {}
            for k in (
                "tax_units",
                "spm_units",
                "families",
                "marital_units",
                "households",
            )
        },
    )
    for i, unit in enumerate(units):
        members = []
        for j, attrs in enumerate(unit):
            name = f"p_{i}_{j}"
            people[name] = {k: {year: v} for k, v in attrs.items()}
            members.append(name)
        filers = [
            m
            for m, a in zip(members, unit)
            if a.get("is_tax_unit_head") or a.get("is_tax_unit_spouse")
        ]
        groups["marital_units"][f"m_{i}"] = {"members": filers or members[:1]}
        for j, m in enumerate(members):
            if m not in (filers or members[:1]):
                groups["marital_units"][f"m_{i}_{j}"] = {"members": [m]}
        for key, prefix in (("tax_units", "t"), ("spm_units", "s"), ("families", "f")):
            groups[key][f"{prefix}_{i}"] = {"members": members}
        groups["households"][f"h_{i}"] = {
            "members": members,
            "state_code": {year: state},
        }
    return {"people": people, **groups}


def _calc(sim, name, year):
    return np.asarray(sim.calculate(name, year), dtype=float)


@st.composite
def borrowers(draw):
    joint = draw(st.booleans())
    head = {
        "age": 30,
        "is_tax_unit_head": True,
        "employment_income": float(draw(st.integers(0, 250_000))),
        "student_loan_interest": float(draw(st.integers(0, 6_000))),
    }
    unit = [head]
    if joint:
        unit.append(
            {
                "age": 30,
                "is_tax_unit_spouse": True,
                "employment_income": float(draw(st.integers(0, 60_000))),
                "student_loan_interest": float(draw(st.integers(0, 3_000))),
            }
        )
    return unit


@SETTINGS
@given(
    st.sampled_from([2021, 2022, 2024, 2026]),
    st.lists(borrowers(), min_size=8, max_size=20),
)
def test_vt_student_loan_subtraction_completes_the_federal_deduction(year, units):
    sim = Simulation(situation=_situation(units, year, "VT"))
    paid = np.array([sum(p["student_loan_interest"] for p in u) for u in units])
    federal = np.asarray(
        sim.calculate("student_loan_interest_ald", year, map_to="tax_unit")
    )
    sub = _calc(sim, "vt_student_loan_interest_subtraction", year)
    agi = _calc(sim, "adjusted_gross_income", year)
    joint = np.array([len(u) == 2 for u in units])
    limit = np.where(joint, 200_000, 120_000)
    assert (sub >= 0).all()
    if year < 2022:
        assert not sub.any()
        return
    within = agi <= limit
    np.testing.assert_allclose(sub[within] + federal[within], paid[within], atol=0.01)
    assert not sub[~within].any()


@SETTINGS
@given(
    st.sampled_from([2023, 2025, 2026]),
    st.lists(st.integers(0, 260_000), min_size=6, max_size=15),
)
def test_vt_ctc_phase_out_is_per_child(year, agis):
    units = []
    for agi in agis:
        for n in (1, 3):
            units.append(
                [{"age": 35, "is_tax_unit_head": True}] + [{"age": 2} for _ in range(n)]
            )
    situation = _situation(units, year, "VT")
    for i, agi in enumerate(np.repeat(agis, 2)):
        situation["tax_units"][f"t_{i}"]["adjusted_gross_income"] = {year: float(agi)}
    sim = Simulation(situation=situation)
    ctc = _calc(sim, "vt_ctc", year).reshape(-1, 2)
    np.testing.assert_allclose(ctc[:, 1], 3 * ctc[:, 0], atol=0.01)


@SETTINGS
@given(
    st.sampled_from([2022, 2024, 2025, 2026]),
    st.lists(
        st.tuples(st.integers(0, 3_000), st.integers(0, 3_000), st.integers(1, 3)),
        min_size=6,
        max_size=15,
    ),
)
def test_ut_at_home_parent_credit_once_per_return(year, draws):
    units = []
    for head_earnings, spouse_earnings, newborns in draws:
        kids = [{"age": 0} for _ in range(newborns)]
        # The spouse qualifies in the first copy (earnings <= $3,000) and not
        # in the second ($10,000), with total income kept under $50,000.
        for spouse_pay in (float(spouse_earnings), 10_000.0):
            units.append(
                [
                    {
                        "age": 30,
                        "is_tax_unit_head": True,
                        "employment_income": float(head_earnings),
                    },
                    {
                        "age": 30,
                        "is_tax_unit_spouse": True,
                        "employment_income": spouse_pay,
                    },
                ]
                + kids
            )
    sim = Simulation(situation=_situation(units, year, "UT"))
    credit = _calc(sim, "ut_at_home_parent_credit_potential", year).reshape(-1, 2)
    np.testing.assert_allclose(credit[:, 0], credit[:, 1], atol=0.01)


@st.composite
def homestead_couples(draw):
    def adult():
        return {
            "age": draw(st.integers(16, 80)),
            "is_disabled": draw(st.booleans()),
            "employment_income": float(draw(st.sampled_from([0, 0, 500, 3_000]))),
            "real_estate_taxes": float(draw(st.integers(0, 1_500))),
        }

    return adult(), adult()


@SETTINGS
@given(
    st.sampled_from([2021, 2023, 2025]),
    st.lists(homestead_couples(), min_size=6, max_size=12),
)
def test_wi_homestead_eligibility_is_label_free_and_monotone(year, couples):
    # Per couple: labels (a head, b head) x claims (none, a, b, both).
    units = []
    for a, b in couples:
        for claims in [(False, False), (True, False), (False, True), (True, True)]:
            for a_is_head in (True, False):
                pa = {**a, "claimed_as_dependent_on_another_return": claims[0]}
                pb = {**b, "claimed_as_dependent_on_another_return": claims[1]}
                first, second = (pa, pb) if a_is_head else (pb, pa)
                units.append(
                    [
                        {**first, "is_tax_unit_head": True},
                        {**second, "is_tax_unit_spouse": True},
                    ]
                )
    sim = Simulation(situation=_situation(units, year, "WI"))
    eligible = _calc(sim, "wi_homestead_eligible", year).reshape(-1, 4, 2)
    np.testing.assert_array_equal(eligible[:, :, 0], eligible[:, :, 1])
    e = eligible[:, :, 0]
    none, a_claimed, b_claimed, both = e.T
    for more, fewer in (
        (a_claimed, none),
        (b_claimed, none),
        (both, a_claimed),
        (both, b_claimed),
    ):
        assert not (more > fewer).any()
