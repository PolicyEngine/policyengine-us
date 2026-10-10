"""Invariants for dependents' income in the filer's net investment income.

26 USC 1411(a)(1) taxes each individual's own net investment income, so a tax
unit dependent's interest, dividends, rents, passive income and capital gains
go on the dependent's own Form 8960. A parent's Form 8960 picks up a child's
interest, dividends and capital gain distributions only through a Form 8814
election (Form 8960 line 7), which the model does not implement. So
`net_investment_income` counts the head and spouse only, as `irs_gross_income`
does for AGI.

Each property must hold for every tax unit, so the tests draw a seeded random
population of tax units (single, head of household with dependents, joint with
and without dependents) plus deterministic edge rows. Each scenario runs as one
vectorized simulation:

1. Dependents' investment income inputs, of either sign, never change the
   filer's `net_investment_income`, `filer_loss_limited_net_capital_gains`,
   AGI, NIIT MAGI or `net_investment_income_tax`.
2. `net_investment_income` equals an independent numpy computation over the
   head and spouse: their interest, dividends, rents (including Form 4835
   farm rent), passive pass-through, estate and trust income, plus their
   netted Schedule D gain or loss with capital gain distributions on line 13,
   limited under 26 USC 1211(b).
3. -loss limit <= `filer_loss_limited_net_capital_gains`, and it equals
   `loss_limited_net_capital_gains` when the unit has no dependents.
4. For tax units without dependents, `net_investment_income` equals the
   all-member formula (person-level sources plus
   `loss_limited_net_capital_gains`), so leaving dependents out changes
   nothing for filers without dependents.
5. 0 <= NIIT = 3.8% x min(max(0, NII), max(0, MAGI - threshold)).
"""

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEARS = [2024, 2025]
N_RANDOM = 300
SEED = 20261004
TOLERANCE = 0.01  # dollars

# Person-level inputs that feed net_investment_income. Passive pass-through
# income is drawn as a share of partnership_s_corp_income below.
SIGNED_INPUTS = [
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "short_term_capital_gains",
    "long_term_capital_gains",
]
NONNEGATIVE_INPUTS = [
    "taxable_interest_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
    "non_sch_d_capital_gains",
]
INPUTS = (
    SIGNED_INPUTS
    + NONNEGATIVE_INPUTS
    + ["partnership_s_corp_income", "passive_partnership_s_corp_income"]
)
# Schedule D gains and losses, with capital gain distributions (line 13).
CAPITAL_INPUTS = [
    "short_term_capital_gains",
    "long_term_capital_gains",
    "non_sch_d_capital_gains",
]
# Every person-level amount Form 8960 counts, other than Schedule D gains.
NII_PERSON_INPUTS = [
    "taxable_interest_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
    "rental_income",
    "farm_rent_income",
    "passive_partnership_s_corp_income",
    "estate_income",
]
OUTPUTS = [
    "net_investment_income",
    "net_investment_income_tax",
    "filer_loss_limited_net_capital_gains",
    "loss_limited_net_capital_gains",
    "adjusted_gross_income",
    "niit_magi",
]


def _draw_amounts(rng, scale):
    """Whole-dollar amounts with many zeros; signed inputs take either sign."""
    amounts = {}
    for name in SIGNED_INPUTS:
        amounts[name] = float(
            round(
                rng.choice(
                    [0.0, rng.uniform(-scale, 0), rng.uniform(0, scale)],
                    p=[0.5, 0.2, 0.3],
                )
            )
        )
    for name in NONNEGATIVE_INPUTS:
        amounts[name] = float(
            round(rng.choice([0.0, rng.uniform(0, scale)], p=[0.5, 0.5]))
        )
    partnership = float(
        round(
            rng.choice(
                [0.0, rng.uniform(-scale, 0), rng.uniform(0, scale)],
                p=[0.5, 0.2, 0.3],
            )
        )
    )
    amounts["partnership_s_corp_income"] = partnership
    amounts["passive_partnership_s_corp_income"] = float(
        round(partnership * rng.choice([0.0, 0.5, 1.0]))
    )
    return amounts


def _draw_units():
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(N_RANDOM):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "kind": kind,
                # Wages around the NIIT thresholds make the MAGI limb bind in
                # some units and the NII limb in others.
                "head_wages": float(round(rng.uniform(0, 450_000))),
                "head": _draw_amounts(rng, 80_000.0),
                "spouse": (
                    _draw_amounts(rng, 60_000.0) if kind.startswith("joint") else None
                ),
                "dependents": [
                    _draw_amounts(rng, 80_000.0) for _ in range(n_dependents)
                ],
            }
        )
    zero = {name: 0.0 for name in INPUTS}
    units += [
        # The dependent's interest would push NII up to the excess MAGI.
        {"kind": "hoh", "head_wages": 300_000.0,
         "head": {**zero, "taxable_interest_income": 10_000.0},
         "spouse": None,
         "dependents": [{**zero, "taxable_interest_income": 200_000.0}]},
        # The dependent's gain would absorb the head's capital loss.
        {"kind": "hoh", "head_wages": 300_000.0,
         "head": {**zero, "long_term_capital_gains": -10_000.0},
         "spouse": None,
         "dependents": [{**zero, "long_term_capital_gains": 10_000.0}]},
        # The dependent's capital loss would reduce the head's gain.
        {"kind": "hoh", "head_wages": 300_000.0,
         "head": {**zero, "long_term_capital_gains": 10_000.0},
         "spouse": None,
         "dependents": [{**zero, "short_term_capital_gains": -3_000.0}]},
        # Joint filers: the spouse's loss nets against the head's gain.
        {"kind": "joint_dependents", "head_wages": 300_000.0,
         "head": {**zero, "long_term_capital_gains": 10_000.0},
         "spouse": {**zero, "short_term_capital_gains": -4_000.0},
         "dependents": [{**zero, "rental_income": 25_000.0}]},
    ]  # fmt: skip
    return units


def _situation(units, year, *, zero_dependents=False):
    people, tax_units, households = {}, {}, {}
    for i, u in enumerate(units):
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": {year: 45},
            "is_tax_unit_head": {year: True},
            "employment_income": {year: u["head_wages"]},
            **{name: {year: value} for name, value in u["head"].items()},
        }
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            members.append(spouse)
            people[spouse] = {
                "age": {year: 44},
                "is_tax_unit_spouse": {year: True},
                **{name: {year: value} for name, value in u["spouse"].items()},
            }
        factor = 0.0 if zero_dependents else 1.0
        for j, amounts in enumerate(u["dependents"]):
            child = f"child_{i}_{j}"
            members.append(child)
            people[child] = {
                "age": {year: 12 + j},
                "is_tax_unit_dependent": {year: True},
                **{name: {year: factor * value} for name, value in amounts.items()},
            }
        tax_units[f"tu_{i}"] = {"members": members}
        households[f"hh_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


def _by_person(units, key):
    """Person-level input arrays in simulation member order."""
    rows = []
    for u in units:
        rows.append((u["head"], False))
        if u["spouse"] is not None:
            rows.append((u["spouse"], False))
        rows += [(amounts, True) for amounts in u["dependents"]]
    if key == "is_dependent":
        return np.array([dependent for _, dependent in rows])
    return np.array([amounts[key] for amounts, _ in rows])


@pytest.fixture(scope="module")
def units():
    return _draw_units()


@pytest.fixture(scope="module")
def reference_parameters():
    # The reference calculations only read policy. Build an independent model
    # once per module instead of rebuilding it for each assertion and year.
    return CountryTaxBenefitSystem().parameters


@pytest.fixture(scope="module", params=YEARS)
def runs(request, units, reference_parameters):
    year = request.param
    out = {
        "year": year,
        "irs": reference_parameters(f"{year}-01-01").gov.irs,
    }
    for name, kwargs in {"with": {}, "no_dependent": {"zero_dependents": True}}.items():
        sim = Simulation(situation=_situation(units, year, **kwargs))
        out[name] = {
            v: np.asarray(sim.calculate(v, year), dtype=float) for v in OUTPUTS
        }
        out[name]["is_tax_unit_dependent"] = np.asarray(
            sim.calculate("is_tax_unit_dependent", year)
        )
        out[name]["filing_status"] = sim.calculate("filing_status", year)
        out[name]["person_tax_unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _unit_sum(runs, person_values):
    return np.bincount(
        runs["with"]["person_tax_unit"],
        weights=person_values,
        minlength=len(runs["with"]["net_investment_income"]),
    )


def _loss_limit(runs):
    return runs["irs"].capital_gains.loss_limit[runs["with"]["filing_status"]]


def test_dependent_flags_match_the_draw(runs, units):
    assert np.array_equal(
        runs["with"]["is_tax_unit_dependent"], _by_person(units, "is_dependent")
    )


def test_dependents_income_stays_off_filer_form_8960(runs, units):
    dependent = _by_person(units, "is_dependent")
    has_dependent_items = _unit_sum(
        runs,
        dependent * sum(np.abs(_by_person(units, name)) for name in INPUTS),
    )
    assert (has_dependent_items > 0).sum() > 100
    for variable in [
        "net_investment_income",
        "filer_loss_limited_net_capital_gains",
        "adjusted_gross_income",
        "niit_magi",
        "net_investment_income_tax",
    ]:
        np.testing.assert_allclose(
            runs["with"][variable],
            runs["no_dependent"][variable],
            atol=TOLERANCE,
            err_msg=variable,
        )


def test_net_investment_income_matches_reference(runs, units):
    """Differential check against an independent numpy computation."""
    filer = ~_by_person(units, "is_dependent")
    person_nii = sum(_by_person(units, name) for name in NII_PERSON_INPUTS)
    schedule_d = _unit_sum(
        runs, filer * sum(_by_person(units, name) for name in CAPITAL_INPUTS)
    )
    expected = _unit_sum(runs, filer * person_nii) + np.maximum(
        -_loss_limit(runs), schedule_d
    )
    np.testing.assert_allclose(
        runs["with"]["net_investment_income"], expected, atol=TOLERANCE
    )


def test_filer_capital_gains_within_loss_limit(runs, units):
    filer_gains = runs["with"]["filer_loss_limited_net_capital_gains"]
    assert np.all(filer_gains >= -_loss_limit(runs) - TOLERANCE)
    no_dependents = np.array([not u["dependents"] for u in units])
    assert no_dependents.sum() > 100
    np.testing.assert_allclose(
        filer_gains[no_dependents],
        runs["with"]["loss_limited_net_capital_gains"][no_dependents],
        atol=TOLERANCE,
    )


def test_units_without_dependents_match_all_member_formula(runs, units):
    """Differential check against the all-member formula."""
    person_nii = sum(_by_person(units, name) for name in NII_PERSON_INPUTS)
    old = _unit_sum(runs, person_nii) + runs["with"]["loss_limited_net_capital_gains"]
    no_dependents = np.array([not u["dependents"] for u in units])
    np.testing.assert_allclose(
        runs["with"]["net_investment_income"][no_dependents],
        old[no_dependents],
        atol=TOLERANCE,
    )


def test_niit_within_statutory_bounds(runs):
    p = runs["irs"].investment.net_investment_income_tax
    threshold = p.threshold[runs["with"]["filing_status"]]
    nii = runs["with"]["net_investment_income"]
    excess_magi = np.maximum(0, runs["with"]["niit_magi"] - threshold)
    niit = runs["with"]["net_investment_income_tax"]
    assert np.all(niit >= -TOLERANCE)
    assert np.all(niit <= p.rate * np.maximum(0, nii) + TOLERANCE)
    np.testing.assert_allclose(
        niit, p.rate * np.minimum(np.maximum(0, nii), excess_magi), atol=TOLERANCE
    )
    # Both limbs of section 1411(a)(1) bind somewhere in the population.
    assert ((nii > 0) & (excess_magi > 0) & (nii < excess_magi)).sum() > 10
    assert ((nii > 0) & (excess_magi > 0) & (nii > excess_magi)).sum() > 10
