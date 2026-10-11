"""Property tests: whose amounts count in Michigan household resources.

MCL 206.508(3): "'Household' means a claimant and spouse." MCL 206.508(4)
counts "all income received by all persons of a household". The MI-1040CR
asks for "all taxable and nontaxable income you and your spouse received"
(2025 MI-1040 book, page 31), so a dependent's own income and Schedule 1
adjustments are on the dependent's return, not the claimant's. The form
counts amounts the claimant receives for others in the household on three
lines (page 32):

- line 21: Social Security, SSI and railroad retirement benefits, including
  "amounts received for minor children or other dependent adults who live
  with you";
- line 22: child support and foster parent payments;
- line 27: payments to the household by MDHHS and other public assistance.

Line 31 is "insurance premiums you paid for yourself and your family"; a
premium on any member's record is read as one the claimant or spouse paid
for the family's coverage.

So for every household:

1. mi_household_resources equals a reference written from the form: the head
   and spouse's lines 14 to 20 and 23 to 26 and their line 30 adjustments,
   plus every member's lines 21, 22 and 27, less every member's premiums,
   floored at zero.
2. A dependent's own income and adjustments do not matter: zeroing them
   leaves household resources unchanged.
3. Amounts received for the household count wherever they are recorded:
   moving a dependent's line 21, 22 or 27 amount, or premium, to the head
   leaves household resources unchanged.
4. Raising a dependent's line 21, 22 or 27 amount by d raises household
   resources by between 0 and d, and by exactly d when they were positive.
5. Each of the spouse's own sources adds what it adds on the head.
6. The lists are reformable: a source moved into
   household_resources_all_members counts for every member, and an SPM unit
   source in household_resources counts in full.

Every generated household has a dependent, so properties 2 to 4 always bind,
and property 4 always includes a household with positive resources.

Comparisons allow one cent or eight float32 spacings at the sum of the
household's absolute amounts, as in test_mi_household_resources_losses.py.
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

# Inputs that are the claimant's or spouse's own, by MI-1040CR line.
CLAIMANT_LINES = {
    "employment_income_before_lsr": 14,
    "strike_benefits": 14,
    "disability_benefits": 14,
    "taxable_interest_income": 15,
    "tax_exempt_interest_income": 15,
    "qualified_dividend_income": 15,
    "self_employment_income": 16,
    "s_corp_income": 16,
    "rental_income": 17,
    "taxable_pension_income": 18,
    "long_term_capital_gains": 19,
    "alimony_income": 20,
    "gambling_winnings": 20,
    "unemployment_compensation": 23,
    "miscellaneous_income": 24,
    "veterans_benefits": 26,
    "workers_compensation": 26,
    # Guaranteed income pilot payments: the recipient's own (line 25).
    "gi_cash_assistance": 25,
    # Line 30: penalty on early withdrawal of savings (Schedule 1 line 18).
    "early_withdrawal_penalty": 30,
}
# Inputs the claimant receives for the household, by MI-1040CR line.
HOUSEHOLD_LINES = {
    "social_security_retirement": 21,
    "social_security_survivors": 21,
    "ssi": 21,
    "railroad_benefits": 21,
    "child_support_received": 22,
    "general_assistance": 27,
}
PREMIUMS = "health_insurance_premiums"
# Sources that can be negative.
SIGNED = {"self_employment_income", "s_corp_income", "rental_income"}
SIGNED.add("long_term_capital_gains")
PERSON_INPUTS = [*CLAIMANT_LINES, *HOUSEHOLD_LINES, PREMIUMS]
# Person-level line 30 amounts read from the model.
PERSON_ADJUSTMENTS = [
    "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald_person",
]


def zero_person():
    return {name: 0 for name in PERSON_INPUTS}


def build_situation(households):
    """One Michigan tax unit per household: a head aged 45, an optional
    spouse aged 44, and dependents aged 10 or 16 (children) or 75 (a
    dependent parent). The SPM unit is the tax unit, and its Family
    Independence Program grant (tanf) is an input, so the model does not
    compute one from the household's income."""
    people, tax_units, marital_units, households_out = {}, {}, {}, {}
    spm_units = {}
    for i, h in enumerate(households):
        members, couple = [], []
        roles = [("head", h["head"])]
        if h.get("spouse") is not None:
            roles.append(("spouse", h["spouse"]))
        roles += [("dependent", d) for d in h.get("dependents", [])]
        for j, (role, p) in enumerate(roles):
            name = f"person_{i}_{j}"
            age = {"head": 45, "spouse": 44}.get(role, p.get("age", 10))
            person = {"age": {YEAR: age}}
            for variable in PERSON_INPUTS:
                person[variable] = {YEAR: p.get(variable, 0)}
            # Roles are set for everyone: an adult dependent would otherwise
            # be the spouse, and a variable input for some people gives the
            # others its default value, not its formula.
            person["is_tax_unit_head"] = {YEAR: role == "head"}
            person["is_tax_unit_spouse"] = {YEAR: role == "spouse"}
            person["is_tax_unit_dependent"] = {YEAR: role == "dependent"}
            people[name] = person
            members.append(name)
            if role == "dependent":
                marital_units[f"marital_unit_{i}_{j}"] = {"members": [name]}
            else:
                couple.append(name)
        tax_units[f"tax_unit_{i}"] = {"members": members}
        spm_units[f"spm_unit_{i}"] = {
            "members": members,
            "tanf": {YEAR: h.get("tanf", 0)},
        }
        marital_units[f"marital_unit_{i}"] = {"members": couple}
        households_out[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "MI"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "households": households_out,
    }


def filers(h):
    return [h["head"]] + ([h["spouse"]] if h.get("spouse") is not None else [])


def everyone(h):
    return filers(h) + list(h.get("dependents", []))


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    result = np.asarray(simulation.calculate("mi_household_resources", YEAR))
    # Each person's model amounts for the line 30 self-employment
    # adjustments, in situation order.
    adjustments = sum(
        np.asarray(simulation.calculate(name, YEAR)) for name in PERSON_ADJUSTMENTS
    )
    per_household, k = [], 0
    for h in households:
        n = len(everyone(h))
        per_household.append(adjustments[k : k + n])
        k += n
    return result, per_household


def amount(people, names):
    return sum(p.get(name, 0) for p in people for name in names)


def by_line(lines, *wanted):
    return [name for name, line in lines.items() if line in wanted]


def reference(h, person_adjustments):
    """MI-1040CR line 33 from the form."""
    own = filers(h)
    line_14 = amount(own, by_line(CLAIMANT_LINES, 14))
    line_15 = amount(own, by_line(CLAIMANT_LINES, 15))
    line_16 = max(0, amount(own, ["self_employment_income", "s_corp_income"]))
    line_17 = max(0, amount(own, ["rental_income"]))
    line_18 = amount(own, by_line(CLAIMANT_LINES, 18))
    line_19 = max(-CAPITAL_LOSS_LIMIT, amount(own, ["long_term_capital_gains"]))
    lines_20_to_26 = amount(own, by_line(CLAIMANT_LINES, 20, 23, 24, 25, 26))
    received = amount(everyone(h), list(HOUSEHOLD_LINES))
    # Line 27: the household's Family Independence Program grant, in full.
    received += h.get("tanf", 0)
    # Line 30: the head and spouse come first in each household's slice.
    line_30 = float(sum(person_adjustments[: len(own)]))
    line_30 += amount(own, ["early_withdrawal_penalty"])
    line_31 = amount(everyone(h), [PREMIUMS])
    total = line_14 + line_15 + line_16 + line_17 + line_18 + line_19
    total += lines_20_to_26 + received
    return max(0, total - line_30 - line_31)


def tolerance(h):
    """One cent, or eight float32 spacings at the sum of the household's
    absolute amounts."""
    scale = sum(abs(v) for p in everyone(h) for v in p.values())
    scale += abs(h.get("tanf", 0))
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))


def copy(h):
    out = {"head": dict(h["head"]), "tanf": h.get("tanf", 0)}
    if h.get("spouse") is not None:
        out["spouse"] = dict(h["spouse"])
    out["dependents"] = [dict(d) for d in h.get("dependents", [])]
    return out


def without_dependents_own_amounts(h):
    out = copy(h)
    for d in out["dependents"]:
        for name in CLAIMANT_LINES:
            d[name] = 0
    return out


def with_household_amounts_on_head(h):
    out = copy(h)
    for d in out["dependents"]:
        for name in [*HOUSEHOLD_LINES, PREMIUMS]:
            out["head"][name] = out["head"].get(name, 0) + d.get(name, 0)
            d[name] = 0
    return out


def assert_properties(households):
    """Properties 1, 2 and 3. The modified copies go in the same
    simulation."""
    zeroed = [without_dependents_own_amounts(h) for h in households]
    moved = [with_household_amounts_on_head(h) for h in households]
    result, adjustments = calculate(households + zeroed + moved)
    n = len(households)
    for i, h in enumerate(households):
        tol = tolerance(h)
        # 1. The form.
        assert result[i] == pytest.approx(reference(h, adjustments[i]), abs=tol), h
        assert result[i] >= 0, h
        # 2. A dependent's own income and adjustments do not count.
        assert result[n + i] == pytest.approx(result[i], abs=tol), h
        # 3. Amounts received for the household count wherever recorded.
        assert result[2 * n + i] == pytest.approx(result[i], abs=tol), h


# ---------------------------------------------------------------------------
# Deterministic tests (no Hypothesis needed).
# ---------------------------------------------------------------------------


def base_household(dependent_age=10, spouse=False):
    head = zero_person()
    head["employment_income_before_lsr"] = 40_000
    return {
        "head": head,
        "spouse": zero_person() if spouse else None,
        "dependents": [dict(zero_person(), age=dependent_age)],
    }


def test_each_source_for_a_dependent():
    """For a child and for a dependent parent, every source on its own: a
    dependent's own income and adjustments leave household resources at the
    base, and an amount received for the household adds in full, as it
    would for the head."""
    households, cases = [], []
    for age, spouse in itertools.product([10, 75], [False, True]):
        base = base_household(age, spouse)
        households.append(base)
        cases.append((age, spouse, None, 0))
        for name in PERSON_INPUTS:
            values = [7_000, -7_000] if name in SIGNED else [7_000]
            for value in values:
                h = copy(base)
                h["dependents"][0][name] = value
                households.append(h)
                cases.append((age, spouse, name, value))
                if name in HOUSEHOLD_LINES or name == PREMIUMS:
                    on_head = copy(base)
                    on_head["head"][name] = value
                    households.append(on_head)
                    cases.append((age, spouse, f"head:{name}", value))
    result, adjustments = calculate(households)
    base_result = {}
    for i, (age, spouse, name, value) in enumerate(cases):
        if name is None:
            base_result[(age, spouse)] = result[i]
    head_result = {
        (age, spouse, name[5:], value): result[i]
        for i, (age, spouse, name, value) in enumerate(cases)
        if name is not None and name.startswith("head:")
    }
    for i, (age, spouse, name, value) in enumerate(cases):
        h = households[i]
        assert result[i] == pytest.approx(
            reference(h, adjustments[i]), abs=TOLERANCE
        ), cases[i]
        if name is None or name.startswith("head:"):
            continue
        base = base_result[(age, spouse)]
        if name in CLAIMANT_LINES:
            assert result[i] == pytest.approx(base, abs=TOLERANCE), cases[i]
        elif name in HOUSEHOLD_LINES:
            assert result[i] == pytest.approx(base + value, abs=TOLERANCE)
            assert result[i] == pytest.approx(
                head_result[(age, spouse, name, value)], abs=TOLERANCE
            ), cases[i]
        else:  # Premiums paid for the family.
            assert result[i] == pytest.approx(base - value, abs=TOLERANCE)
            assert result[i] == pytest.approx(
                head_result[(age, spouse, name, value)], abs=TOLERANCE
            ), cases[i]


def test_spouse_counts_like_the_head():
    """Both spouses' own amounts count: each source on the spouse adds what
    it adds on the head."""
    households = []
    for name in CLAIMANT_LINES:
        if name == "early_withdrawal_penalty":
            continue
        on_head = base_household(spouse=True)
        on_head["head"][name] += 7_000
        on_spouse = base_household(spouse=True)
        on_spouse["spouse"][name] = 7_000
        households += [on_head, on_spouse]
    result, adjustments = calculate(households)
    for k in range(0, len(households), 2):
        assert result[k] == pytest.approx(result[k + 1], abs=TOLERANCE)
        assert result[k] == pytest.approx(
            reference(households[k], adjustments[k]), abs=TOLERANCE
        )


def reform_lists(household_resources=None, all_members=None):
    """A reform that replaces Michigan's source lists for the year."""

    class reform(Reform):
        def apply(self):
            def modify(parameters):
                p = parameters.gov.states.mi.tax.income
                for node, values in [
                    (p.household_resources, household_resources),
                    (p.household_resources_all_members, all_members),
                ]:
                    if values is not None:
                        node.update(
                            start=instant(f"{YEAR}-01-01"),
                            stop=instant(f"{YEAR}-12-31"),
                            value=values,
                        )
                return parameters

            self.modify_parameters(modify)

    return reform


def test_reformed_lists():
    """6. A source moved into household_resources_all_members counts for
    every member, and an SPM unit source put in household_resources in place
    of tanf counts in full."""
    h = base_household()
    h["dependents"][0]["gi_cash_assistance"] = 7_000
    baseline = Simulation(situation=build_situation([h]))
    p = baseline.tax_benefit_system.parameters.gov.states.mi.tax.income
    sources = list(p.household_resources(f"{YEAR}-01-01"))
    all_members = list(p.household_resources_all_members(f"{YEAR}-01-01"))
    # The dependent's own pilot payment is not household resources...
    assert baseline.calculate("mi_household_resources", YEAR)[0] == pytest.approx(
        40_000, abs=TOLERANCE
    )
    # ...unless a reform counts it for every member.
    moved = Simulation(
        situation=build_situation([h]),
        reform=reform_lists(all_members=all_members + ["gi_cash_assistance"]),
    )
    assert moved.calculate("mi_household_resources", YEAR)[0] == pytest.approx(
        47_000, abs=TOLERANCE
    )
    # A parent with wages of 10,000 and a child, and an SPM unit grant of
    # 6,000 given as tanf_if_takes_up, which the reform lists in place of tanf.
    family = base_household()
    family["head"]["employment_income_before_lsr"] = 10_000
    situation = build_situation([family])
    situation["spm_units"]["spm_unit_0"]["tanf_if_takes_up"] = {YEAR: 6_000}
    swapped = Simulation(
        situation=situation,
        reform=reform_lists(
            household_resources=[
                "tanf_if_takes_up" if s == "tanf" else s for s in sources
            ],
            all_members=[s for s in all_members if s != "tanf"],
        ),
    )
    assert swapped.calculate("mi_household_resources", YEAR)[0] == pytest.approx(
        16_000, abs=TOLERANCE
    )


# ---------------------------------------------------------------------------
# Hypothesis properties. Hypothesis is a dev extra: without it these tests
# are not collected and the deterministic tests above still run.
# ---------------------------------------------------------------------------

try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    SIGNED_AMOUNT = st.integers(min_value=-200_000, max_value=200_000)
    AMOUNT = st.integers(min_value=100, max_value=100_000)
    SLOW = [hypothesis.HealthCheck.too_slow]

    @st.composite
    def person(draw):
        p = zero_person()
        # Each person draws a few sources, so households are sparse enough
        # that the floor at zero does not hide everything.
        names = draw(st.lists(st.sampled_from(PERSON_INPUTS), max_size=5, unique=True))
        for name in names:
            p[name] = draw(SIGNED_AMOUNT if name in SIGNED else AMOUNT)
        return p

    @st.composite
    def household(draw):
        dependents = []
        for _ in range(draw(st.integers(min_value=1, max_value=2))):
            d = draw(person())
            d["age"] = draw(st.sampled_from([10, 16, 75]))
            dependents.append(d)
        return {
            "head": draw(person()),
            "spouse": draw(st.one_of(st.none(), person())),
            "dependents": dependents,
            "tanf": draw(st.one_of(st.just(0), AMOUNT)),
        }

    @hypothesis.settings(max_examples=50, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(household(), min_size=1, max_size=15))
    def test_properties(households):
        assert_properties(households)

    @hypothesis.settings(max_examples=30, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(
        st.lists(household(), min_size=1, max_size=10),
        st.sampled_from(list(HOUSEHOLD_LINES)),
        st.integers(min_value=1, max_value=50_000),
    )
    def test_more_received_for_a_dependent(households, source, extra):
        """4. More of a line 21, 22 or 27 amount for a dependent raises
        household resources by between 0 and the increase, and by exactly
        the increase when they were positive."""
        # A household with positive resources, so the exact-increase branch
        # always runs.
        households = households + [base_household()]
        raised = []
        for h in households:
            r = copy(h)
            r["dependents"][0][source] = r["dependents"][0].get(source, 0) + extra
            raised.append(r)
        result, _ = calculate(households + raised)
        n = len(households)
        for i, h in enumerate(raised):
            tol = tolerance(h)
            change = float(result[n + i]) - float(result[i])
            assert -tol <= change <= extra + tol, (households[i], source)
            if result[i] > tol:
                assert change == pytest.approx(extra, abs=tol), (
                    households[i],
                    source,
                )
