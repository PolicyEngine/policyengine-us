"""Property tests: business and rental losses in Michigan household resources.

MCL 206.508(4) defines total household resources as income "increased by the
following deductions from federal gross income: (a) Any net business loss
after netting all business income and loss. (b) Any net rental or royalty
loss." The 2025 MI-1040 book (page 26) puts it as "AGI, excluding net business
and farm losses, net rent and royalty losses". On the MI-1040CR:

- line 16 nets U.S. Schedule C, Form 4797 Part II, Schedule E Parts II and III
  and Schedule F, and line 17 nets Schedule E Parts I, IV (REMIC income, which
  has no input) and V; "If the total is negative enter 0";
- line 19 is net capital gains and losses from Schedule D, a loss limited to
  $3,000;
- line 30 is "total adjustments from your U.S. Form 1040, Schedule 1"
  (Part II). Business, rental and capital losses are income items, not
  adjustments, so loss_ald does not enter it;
- line 31 is health insurance premiums.

The household is "a claimant and spouse" (MCL 206.508(3)).

So for every combination of business, rental and capital gains and losses:

1. mi_household_resources = max(0, wages + max(0, line 16 sources) +
   max(0, line 17 sources) + max(-3,000, capital gains) - Schedule 1
   adjustments - premiums), where the adjustments here are the deduction for
   self-employment tax and the early withdrawal penalty.
2. It does not depend on loss_ald: a reform that takes loss_ald out of
   gov.irs.ald.deductions changes AGI but not household resources (checked on
   the grid, which builds the reform once).
3. Losses stay in their own line. When every line 16 source is zero or
   negative, the result equals the result with them all set to zero; the
   same holds for line 17.
4. Household resources are between zero and the sum of the positive income
   amounts.
5. Raising a source that carries no self-employment tax (S corporation,
   estate, Form 4797, rental or farm rental income) by d raises household
   resources by between 0 and d. Schedule C and Schedule F income are left
   out on purpose: when line 16 is floored at zero, more Schedule C income
   still raises the deduction for self-employment tax on line 30, so
   household resources fall. The form gives that result.
6. A dependent's business and rental losses and S corporation, estate and
   rental income leave household resources unchanged.

Amounts are whole dollars of at most $500,000, and the self-employment tax
deduction is read from the model. The model computes in single precision, so a
comparison allows one cent or eight float32 spacings at the sum of the
household's absolute amounts, whichever is larger: $0.25 for a household whose
amounts add up to $500,000, and up to about $4 for the largest two-person
households drawn. The early withdrawal penalty and premiums are drawn as zero
or at least $100, so leaving either out would exceed the tolerance.
"""

import itertools

import numpy as np
import pytest

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2025
CAPITAL_LOSS_LIMIT = 3_000
TOLERANCE = 0.01

PERSON_LINE_16 = [
    "self_employment_income",
    "farm_operations_income",
    "s_corp_income",
    "estate_income",
]
PERSON_LINE_17 = ["rental_income", "farm_rent_income"]
PERSON_INPUTS = [
    "employment_income_before_lsr",
    *PERSON_LINE_16,
    *PERSON_LINE_17,
    "long_term_capital_gains",
    "early_withdrawal_penalty",
    "health_insurance_premiums",
]
# Form 4797 Part II, a tax unit input.
UNIT_LINE_16 = ["other_net_gain"]
# Sources without self-employment tax, for property 5.
NO_SE_TAX_SOURCES = ["s_corp_income", "estate_income", "rental_income"]
NO_SE_TAX_SOURCES += ["farm_rent_income", "other_net_gain"]


def zero_person():
    return {name: 0 for name in PERSON_INPUTS}


def build_situation(households):
    """One Michigan tax unit per household: one adult (single) or two
    (joint), any dependents (aged 15), and the tax unit's Form 4797 amount."""
    people, tax_units, marital_units, households_out = {}, {}, {}, {}
    for i, h in enumerate(households):
        adults, members = [], []
        dependents = h.get("dependents", [])
        for j, (p, age) in enumerate(
            [(p, 45) for p in h["people"]] + [(p, 15) for p in dependents]
        ):
            name = f"person_{i}_{j}"
            people[name] = {"age": {YEAR: age}}
            for variable in PERSON_INPUTS:
                people[name][variable] = {YEAR: p[variable]}
            members.append(name)
            if age == 45:
                adults.append(name)
            else:
                marital_units[f"marital_unit_{i}_{j}"] = {"members": [name]}
        # Set on every unit: a variable input for some units gives the
        # others its default value, not its formula.
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "other_net_gain": {YEAR: h["other_net_gain"]},
        }
        marital_units[f"marital_unit_{i}"] = {"members": adults}
        households_out[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "MI"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households_out,
    }


def without_loss_ald():
    """A reform that removes loss_ald from gov.irs.ald.deductions."""

    class reform(Reform):
        def apply(self):
            def modify(parameters):
                deductions = parameters.gov.irs.ald.deductions
                values = [d for d in deductions(f"{YEAR}-01-01") if d != "loss_ald"]
                deductions.update(
                    start=instant(f"{YEAR}-01-01"),
                    stop=instant(f"{YEAR}-12-31"),
                    value=values,
                )
                return parameters

            self.modify_parameters(modify)

    return reform


OUTPUTS = [
    "mi_household_resources",
    "self_employment_tax_ald",
    "adjusted_gross_income",
]


def calculate(households, reform=None):
    simulation = Simulation(situation=build_situation(households), reform=reform)
    results = {v: np.asarray(simulation.calculate(v, YEAR)) for v in OUTPUTS}
    # Line 30 summed directly, as the formula does: subtracting a large
    # loss_ald from above_the_line_deductions would lose cents in float32.
    deductions = simulation.tax_benefit_system.parameters.gov.irs.ald.deductions
    results["schedule_1_adjustments"] = sum(
        np.asarray(simulation.calculate(d, YEAR, map_to="tax_unit"))
        for d in deductions(f"{YEAR}-01-01")
        if d != "loss_ald"
    )
    return results


def tolerance(h):
    """One cent, or eight float32 spacings at the sum of the household's
    absolute amounts."""
    people = h["people"] + h.get("dependents", [])
    scale = sum(abs(v) for p in people for v in p.values())
    scale += abs(h["other_net_gain"])
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))


def total(h, names):
    return sum(p[name] for p in h["people"] for name in names)


def reference(h, self_employment_tax_ald):
    """MI-1040CR line 33, total household resources, from the form, for a
    household without dependents."""
    line_14 = total(h, ["employment_income_before_lsr"])
    line_16 = max(0, total(h, PERSON_LINE_16) + h["other_net_gain"])
    line_17 = max(0, total(h, PERSON_LINE_17))
    line_19 = max(-CAPITAL_LOSS_LIMIT, total(h, ["long_term_capital_gains"]))
    line_30 = self_employment_tax_ald + total(h, ["early_withdrawal_penalty"])
    line_31 = total(h, ["health_insurance_premiums"])
    return max(0, line_14 + line_16 + line_17 + line_19 - line_30 - line_31)


def positive_income(h):
    names = ["employment_income_before_lsr", *PERSON_LINE_16, *PERSON_LINE_17]
    names.append("long_term_capital_gains")
    return sum(max(0, p[name]) for p in h["people"] for name in names) + max(
        0, h["other_net_gain"]
    )


def with_sources_zeroed(h, person_sources, unit_sources):
    out = {
        "people": [dict(p) for p in h["people"]],
        "other_net_gain": h["other_net_gain"],
    }
    for p in out["people"]:
        for name in person_sources:
            p[name] = 0
    if "other_net_gain" in unit_sources:
        out["other_net_gain"] = 0
    return out


def only_losses(h, person_sources, unit_sources):
    return all(p[name] <= 0 for p in h["people"] for name in person_sources) and all(
        h[name] <= 0 for name in unit_sources
    )


def assert_properties(households, check_loss_ald_reform=False):
    """Properties 1, 3 and 4 (and 2 when asked) for households without
    dependents. The zeroed copies for property 3 go in the same simulation."""
    zeroed, zeroed_of = [], []
    for i, h in enumerate(households):
        for person_sources, unit_sources in (
            (PERSON_LINE_16, UNIT_LINE_16),
            (PERSON_LINE_17, []),
        ):
            if only_losses(h, person_sources, unit_sources):
                zeroed.append(with_sources_zeroed(h, person_sources, unit_sources))
                zeroed_of.append(i)
    model = calculate(households + zeroed)
    n = len(households)
    for i, h in enumerate(households):
        result = model["mi_household_resources"][i]
        tol = tolerance(h)
        # 1. The form.
        assert result == pytest.approx(
            reference(h, model["self_employment_tax_ald"][i]), abs=tol
        ), h
        # The only Schedule 1 adjustments in these households are the two
        # the reference uses.
        expected_adjustments = model["self_employment_tax_ald"][i] + total(
            h, ["early_withdrawal_penalty"]
        )
        assert model["schedule_1_adjustments"][i] == pytest.approx(
            expected_adjustments, abs=tol
        ), h
        # 4. Bounds.
        assert 0 <= result <= positive_income(h) + tol, h
    # 3. Losses stay in their own line.
    for k, i in enumerate(zeroed_of):
        assert model["mi_household_resources"][i] == pytest.approx(
            model["mi_household_resources"][n + k], abs=tolerance(households[i])
        ), households[i]
    # 2. Not loss_ald.
    if check_loss_ald_reform:
        no_loss_ald = calculate(households, reform=without_loss_ald())
        for i, h in enumerate(households):
            assert no_loss_ald["mi_household_resources"][i] == pytest.approx(
                model["mi_household_resources"][i], abs=tolerance(h)
            ), h


# ---------------------------------------------------------------------------
# Deterministic tests (no Hypothesis needed).
# ---------------------------------------------------------------------------

GRID_VALUES = [-30_000, 0, 20_000]
GRID_SOURCES = [*PERSON_LINE_16, *PERSON_LINE_17, "other_net_gain"]


def grid_households():
    """Every sign combination of the seven line 16 and 17 sources."""
    households = []
    for values in itertools.product(GRID_VALUES, repeat=len(GRID_SOURCES)):
        person = zero_person()
        person["employment_income_before_lsr"] = 50_000
        amounts = dict(zip(GRID_SOURCES, values))
        for name in [*PERSON_LINE_16, *PERSON_LINE_17]:
            person[name] = amounts[name]
        households.append(
            {"people": [person], "other_net_gain": amounts["other_net_gain"]}
        )
    return households


def test_grid():
    assert_properties(grid_households(), check_loss_ald_reform=True)


def test_worked_example():
    """A Schedule C loss of 10,000 and S corporation income of 30,000 give
    line 16 = 20,000; a rental loss of 30,000 gives line 17 = 0; the business
    loss is not subtracted again on line 30."""
    person = zero_person()
    person.update(
        employment_income_before_lsr=50_000,
        self_employment_income=-10_000,
        s_corp_income=30_000,
        rental_income=-30_000,
    )
    model = calculate([{"people": [person], "other_net_gain": 0}])
    assert model["mi_household_resources"][0] == 70_000
    # Federal AGI deducts both losses: 50,000 + 30,000 - 10,000 - 30,000.
    assert model["adjusted_gross_income"][0] == 40_000


DEPENDENT_VALUES = {
    # Losses only for Schedule C and F: a dependent's self-employment tax
    # deduction is a separate question (it is not on this return either).
    "self_employment_income": [-20_000, 0],
    "farm_operations_income": [-10_000, 0],
    "s_corp_income": [-20_000, 0, 15_000],
    "estate_income": [-5_000, 0, 5_000],
    "rental_income": [-20_000, 0, 15_000],
    "farm_rent_income": [-5_000, 0, 5_000],
}


def test_dependents_business_and_rental_items():
    """6. Households whose claimant has business and rental income and
    losses, with a dependent whose line 16 and 17 amounts take every
    combination below, equal the same households without the dependent's
    amounts."""
    claimants = []
    # Both lines positive, line 16 negative, line 17 negative.
    for s_corp, rent in [(20_000, 15_000), (-30_000, 20_000), (20_000, -30_000)]:
        claimant = zero_person()
        claimant.update(
            employment_income_before_lsr=50_000,
            s_corp_income=s_corp,
            rental_income=rent,
        )
        claimants.append(claimant)
    with_dependent, without = [], []
    names = list(DEPENDENT_VALUES)
    for claimant in claimants:
        for values in itertools.product(*DEPENDENT_VALUES.values()):
            dependent = zero_person()
            dependent.update(dict(zip(names, values)))
            with_dependent.append(
                {"people": [claimant], "dependents": [dependent], "other_net_gain": 0}
            )
            without.append(
                {
                    "people": [claimant],
                    "dependents": [zero_person()],
                    "other_net_gain": 0,
                }
            )
    model = calculate(with_dependent + without)
    n = len(with_dependent)
    result = model["mi_household_resources"]
    np.testing.assert_allclose(result[:n], result[n:], atol=TOLERANCE)
    # The claimant's own lines still net and floor.
    for i, h in enumerate(without):
        assert result[n + i] == pytest.approx(
            reference(h, model["self_employment_tax_ald"][n + i]), abs=TOLERANCE
        ), h


# ---------------------------------------------------------------------------
# Hypothesis properties. Hypothesis is a dev extra: without it these two
# tests are not collected and the deterministic tests above still run.
# ---------------------------------------------------------------------------

try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    AMOUNT = st.integers(min_value=-500_000, max_value=500_000)
    SMALL = st.integers(min_value=-20_000, max_value=20_000)
    NONNEGATIVE = st.integers(min_value=0, max_value=200_000)
    # Each example builds Simulations; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    @st.composite
    def person(draw):
        amounts = draw(st.sampled_from([AMOUNT, SMALL]))
        p = zero_person()
        p["employment_income_before_lsr"] = draw(st.one_of(st.just(0), NONNEGATIVE))
        for name in [*PERSON_LINE_16, *PERSON_LINE_17, "long_term_capital_gains"]:
            p[name] = draw(st.one_of(st.just(0), amounts))
        p["early_withdrawal_penalty"] = draw(
            st.one_of(st.just(0), st.integers(min_value=100, max_value=5_000))
        )
        p["health_insurance_premiums"] = draw(
            st.one_of(st.just(0), st.integers(min_value=100, max_value=10_000))
        )
        return p

    @st.composite
    def household(draw):
        n = draw(st.sampled_from([1, 2]))
        return {
            "people": [draw(person()) for _ in range(n)],
            "other_net_gain": draw(st.one_of(st.just(0), AMOUNT, SMALL)),
        }

    @hypothesis.settings(max_examples=25, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(household(), min_size=1, max_size=20))
    def test_properties(households):
        assert_properties(households)

    @hypothesis.settings(max_examples=25, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(
        st.lists(household(), min_size=1, max_size=10),
        st.sampled_from(NO_SE_TAX_SOURCES),
        st.integers(min_value=1, max_value=100_000),
    )
    def test_more_income_without_self_employment_tax(households, source, extra):
        """5. More S corporation, estate, Form 4797, rental or farm rental
        income raises household resources by between 0 and the increase."""
        raised = []
        for h in households:
            r = {"people": [dict(p) for p in h["people"]]}
            r["other_net_gain"] = h["other_net_gain"]
            if source == "other_net_gain":
                r["other_net_gain"] += extra
            else:
                r["people"][0][source] += extra
            raised.append(r)
        result = calculate(households + raised)["mi_household_resources"]
        n = len(households)
        for i, h in enumerate(raised):
            change = float(result[n + i]) - float(result[i])
            tol = tolerance(h)
            assert -tol <= change <= extra + tol, (households[i], source, extra)
