"""Properties of the elderly or disabled credit (26 U.S.C. 22, Schedule R).

1. A married individual filing a separate return starts from $3,750
   (22(c)(2)(A)(iii)), and the later steps only reduce it, so the section 22
   amount for a separate filer never exceeds $3,750.
2. For every status but separate, the section 22 amount equals the formula
   before the separate-filer change, frozen below as a reference function.
3. For a separate filer it equals the closed form of 22(c)-(e) with the
   model's count of qualifying members (which, like the model, includes
   dependents): zero if the spouses lived together at any time in the
   year (22(e)(1)); otherwise min($3,750 if any member qualifies, the
   22(c)(2)(B) cap), less nontaxable pensions and social security
   (22(c)(3)), less half of AGI over $5,000 (22(d)), floored at zero.

Units may carry a dependent, who can qualify by age, so a separate filer
can count two qualified individuals.

Each Hypothesis example is a batch of tax units run as one vectorized
simulation, so the test checks the formulas on mixed arrays as well.
"""

from hypothesis import HealthCheck, example, given, settings, strategies as st
import numpy as np

from policyengine_us import Simulation

YEAR = 2024
SEPARATE_INITIAL_AMOUNT = 3_750
ONE_QUALIFIED = 5_000
TWO_QUALIFIED = 7_500
ELDERLY_AGE = 65
PHASE_OUT_RATE = 0.5
PHASE_OUT_THRESHOLD = {
    "SINGLE": 7_500,
    "JOINT": 10_000,
    "SEPARATE": 5_000,
    "HEAD_OF_HOUSEHOLD": 7_500,
}

FILING_STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD"]

money = st.one_of(st.just(0.0), st.floats(0, 60_000).map(round))

case = st.fixed_dictionaries(
    {
        "filing_status": st.sampled_from(FILING_STATUSES),
        "cohabitating": st.booleans(),
        "head_age": st.integers(40, 90),
        "spouse_age": st.integers(40, 90),
        "head_disabled": st.booleans(),
        "wages": money,
        "pension": money,
        "taxable_share": st.floats(0, 1),
        "social_security": money,
        "disability_payments": st.floats(0, 10_000).map(round),
        # Two in three units have a dependent, half of them 65 or older, so
        # separate filers with two qualified members come up often.
        "dependent_age": st.one_of(st.none(), st.integers(65, 90), st.integers(10, 64)),
    }
)


def build_situation(cases):
    people, tax_units, households = {}, {}, {}
    for i, c in enumerate(cases):
        head = f"head_{i}"
        pension = c["pension"]
        people[head] = {
            "age": {YEAR: c["head_age"]},
            "retired_on_total_disability": {YEAR: c["head_disabled"]},
            "employment_income": {YEAR: c["wages"]},
            "total_disability_payments": {
                YEAR: min(c["disability_payments"], c["wages"])
            },
            "pension_income": {YEAR: pension},
            "taxable_pension_income": {YEAR: round(pension * c["taxable_share"])},
            "social_security_retirement": {YEAR: c["social_security"]},
        }
        members = [head]
        if c["filing_status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {YEAR: c["spouse_age"]}}
            members.append(spouse)
        if c["dependent_age"] is not None:
            dependent = f"dependent_{i}"
            people[dependent] = {
                "age": {YEAR: c["dependent_age"]},
                "is_tax_unit_dependent": {YEAR: True},
            }
            members.append(dependent)
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {YEAR: c["filing_status"]},
            "cohabitating_spouses": {YEAR: c["cohabitating"]},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


def reduction_and_cap_inputs(sim):
    """Per-unit inputs shared by both reference formulas, read from the
    simulation so that only the section 22 step itself is reimplemented."""
    age = sim.calculate("age", YEAR)
    disabled = sim.calculate("retired_on_total_disability", YEAR)
    dependent = sim.calculate("is_tax_unit_dependent", YEAR)
    disability_pay = sim.calculate("total_disability_payments", YEAR)
    elderly = age >= ELDERLY_AGE
    n = sim.map_result(elderly | disabled, "person", "tax_unit")
    num_elderly = sim.map_result(elderly & ~dependent, "person", "tax_unit")
    young_disability = sim.map_result(disability_pay * ~elderly, "person", "tax_unit")
    cap = num_elderly * ONE_QUALIFIED + young_disability
    pensions = sim.map_result(
        sim.calculate("pension_income", YEAR)
        - sim.calculate("taxable_pension_income", YEAR),
        "person",
        "tax_unit",
    )
    social_security = sim.calculate("tax_unit_social_security", YEAR) - sim.calculate(
        "tax_unit_taxable_social_security", YEAR
    )
    agi = sim.calculate("adjusted_gross_income", YEAR)
    return n, cap, pensions + social_security, agi


def pre_change_section_22(n, filing_status, cap, nontaxable, agi):
    """The section 22 formula before the separate-filer change: select took
    n == 1 before the separate-return condition."""
    initial = np.select(
        [n == 1, n == 2, filing_status == "SEPARATE"],
        [ONE_QUALIFIED, TWO_QUALIFIED, SEPARATE_INITIAL_AMOUNT],
        default=0,
    )
    threshold = np.array([PHASE_OUT_THRESHOLD[f] for f in filing_status])
    reduction = PHASE_OUT_RATE * np.maximum(0, agi - threshold)
    return np.maximum(0, np.minimum(initial, cap) - nontaxable - reduction)


def statute_separate_section_22(n, lived_together, cap, nontaxable, agi):
    """26 U.S.C. 22(c)-(e) for a married individual filing separately, counting
    qualifying members as the model does (dependents included)."""
    initial = np.where(n >= 1, SEPARATE_INITIAL_AMOUNT, 0)
    reduction = PHASE_OUT_RATE * np.maximum(0, agi - PHASE_OUT_THRESHOLD["SEPARATE"])
    amount = np.maximum(0, np.minimum(initial, cap) - nontaxable - reduction)
    return np.where(lived_together, 0, amount)


def fixed_case(filing_status, cohabitating, head_age=67, dependent_age=None, **kw):
    c = {
        "filing_status": filing_status,
        "cohabitating": cohabitating,
        "head_age": head_age,
        "spouse_age": 50,
        "head_disabled": False,
        "wages": 3_000.0,
        "pension": 0.0,
        "taxable_share": 0.0,
        "social_security": 0.0,
        "disability_payments": 0.0,
        "dependent_age": dependent_age,
    }
    c.update(kw)
    return c


# A batch that always runs, beside the random ones, so each separate-filer
# branch is reached whatever Hypothesis draws.
FIXED_BATCH = [
    # Separate, lived apart, two qualified members (head and dependent).
    fixed_case("SEPARATE", False, dependent_age=80),
    # Separate, lived together: 22(e)(1) bars the amount.
    fixed_case("SEPARATE", True),
    # Separate, lived together, two qualified members.
    fixed_case("SEPARATE", True, dependent_age=80),
    # Separate, nobody qualifies, with disability pay.
    fixed_case("SEPARATE", False, head_age=60, disability_payments=2_000.0),
    # Joint and single returns whose spouses live together keep the amount.
    fixed_case("JOINT", True),
    fixed_case("SINGLE", True),
    fixed_case("HEAD_OF_HOUSEHOLD", True, dependent_age=70),
    fixed_case("JOINT", False, spouse_age=70, dependent_age=80),
]


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(case, min_size=8, max_size=8))
@example(FIXED_BATCH)
def test_section_22_amount_against_reference_formulas(cases):
    sim = Simulation(situation=build_situation(cases))
    filing_status = sim.calculate("filing_status", YEAR).decode_to_str()
    lived_together = sim.calculate("cohabitating_spouses", YEAR)
    section_22 = sim.calculate("section_22_income", YEAR)
    n, cap, nontaxable, agi = reduction_and_cap_inputs(sim)

    separate = filing_status == "SEPARATE"
    assert (section_22[separate] <= SEPARATE_INITIAL_AMOUNT).all()
    assert (section_22 >= 0).all()

    pre_change = pre_change_section_22(n, filing_status, cap, nontaxable, agi)
    np.testing.assert_allclose(section_22[~separate], pre_change[~separate])

    statute = statute_separate_section_22(n, lived_together, cap, nontaxable, agi)
    np.testing.assert_allclose(section_22[separate], statute[separate])
