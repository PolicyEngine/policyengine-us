"""Invariants for the qualified business income deduction and dependents.

26 USC 199A(a) allows the deduction to the taxpayer, from the qualified
business income of the taxpayer's own trades or businesses (and the spouse's,
on a joint return). A tax unit dependent with business income files their own
return, so the dependent's income, losses and deduction never reach the
filer's: not the sum of per-person amounts, not the loss netting of
199A(c)(2) and Treas. Reg. 1.199A-1(d)(2), and not the 199A(i) minimum.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents, in Texas, Missouri and Iowa),
with business income, losses, W-2 wages and property large enough to reach
the 199A(b)(3) phase-in range; a seeded population adds breadth. Each batch
runs as one vectorized simulation, twice: with the dependents' business
inputs as drawn and with them set to zero. For every tax unit:

1. The dependents' business inputs never change the filer's deduction, its
   per-person shares, the head's and spouse's per-person amounts, the
   Missouri business income deduction or the Iowa deduction.
2. Conservation: the members' shares sum to the deduction, a dependent's
   share is zero, and the members' Iowa deductions sum to Iowa's fraction of
   the federal deduction.
3. Differential: the deduction equals an independent numpy computation of
   the lesser of the head's and spouse's per-person amounts and 20% of
   taxable income less net capital gain, raised from 2026 to the 199A(i)
   minimum on the head's and spouse's eligible QBI; Missouri's equals its
   rate times the head's and spouse's positive QBI.
4. Bounds: the deduction is never negative, never above 20% of taxable
   income less net capital gain (before the minimum), and never above the
   previous all-member sum.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

BUSINESS_INPUTS = [
    "self_employment_income",
    "sstb_self_employment_income",
    "partnership_s_corp_income",
    "rental_income",
    "w2_wages_from_qualified_business",
    "unadjusted_basis_qualified_property",
    "qualified_reit_and_ptp_income",
]
TAX_UNIT_OUTPUTS = [
    "qualified_business_income_deduction",
    "taxable_income_less_qbid",
    "adjusted_net_capital_gain",
    "mo_business_income_deduction",
]
PERSON_OUTPUTS = [
    "qbid_amount",
    "qualified_business_income_deduction_person",
    "qualified_business_income",
    "sstb_qualified_business_income",
    "business_is_sstb",
    "ia_qbi_deduction",
]

money = st.integers(0, 400_000).map(float)


def _maybe(strategy):
    return st.one_of(st.just(0.0), strategy)


@st.composite
def person_amounts(draw):
    return {
        "employment_income": draw(_maybe(money)),
        "self_employment_income": draw(
            _maybe(st.integers(-40_000, 400_000).map(float))
        ),
        "sstb_self_employment_income": draw(
            _maybe(st.integers(-20_000, 300_000).map(float))
        ),
        "partnership_s_corp_income": draw(
            _maybe(st.integers(-30_000, 300_000).map(float))
        ),
        "rental_income": draw(_maybe(st.integers(-10_000, 50_000).map(float))),
        "w2_wages_from_qualified_business": draw(_maybe(money)),
        "unadjusted_basis_qualified_property": draw(_maybe(money)),
        "qualified_reit_and_ptp_income": draw(
            _maybe(st.integers(1, 20_000).map(float))
        ),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "state": draw(st.sampled_from(["TX", "MO", "IA"])),
        "head": draw(person_amounts()),
        "spouse": draw(person_amounts()) if kind.startswith("joint") else None,
        "dependents": [
            {"age": draw(st.integers(5, 23)), **draw(person_amounts())}
            for _ in range(n_dependents)
        ],
    }


SEED = 20261006


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def amounts():
        return {
            "employment_income": some(1, 400_000, 0.6),
            "self_employment_income": some(-40_000, 400_000, 0.6),
            "sstb_self_employment_income": some(-20_000, 300_000, 0.3),
            "partnership_s_corp_income": some(-30_000, 300_000, 0.3),
            "rental_income": some(-10_000, 50_000, 0.2),
            "w2_wages_from_qualified_business": some(1, 400_000, 0.4),
            "unadjusted_basis_qualified_property": some(1, 400_000, 0.3),
            "qualified_reit_and_ptp_income": some(1, 20_000, 0.2),
        }

    units = []
    for _ in range(n):
        kind = str(rng.choice(["single", "hoh", "joint", "joint_dependents"]))
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "state": str(rng.choice(["TX", "MO", "IA"])),
                "head": amounts(),
                "spouse": amounts() if kind.startswith("joint") else None,
                "dependents": [
                    {"age": int(rng.integers(5, 24)), **amounts()}
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


# Roles are inputs, so a drawn dependent with a large income stays a
# dependent rather than failing the dependency tests and joining the return.
HEAD = dict(
    is_tax_unit_head=True, is_tax_unit_spouse=False, is_tax_unit_dependent=False
)
SPOUSE = dict(
    is_tax_unit_head=False, is_tax_unit_spouse=True, is_tax_unit_dependent=False
)
DEPENDENT = dict(
    is_tax_unit_head=False, is_tax_unit_spouse=False, is_tax_unit_dependent=True
)


def _situation(units, year, *, zero_dependents):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {"age": 50, **HEAD, **u["head"]}
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": 48, **SPOUSE, **u["spouse"]}
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            amounts = {k: v for k, v in d.items() if k != "age"}
            if zero_dependents:
                amounts.update({name: 0.0 for name in BUSINESS_INPUTS})
            people[child] = {
                "age": d["age"],
                "is_full_time_student": d["age"] >= 19,
                **DEPENDENT,
                **amounts,
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: u["state"]},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, zero_dependents):
    sim = Simulation(situation=_situation(units, year, zero_dependents=zero_dependents))
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in TAX_UNIT_OUTPUTS + PERSON_OUTPUTS
    }
    out["is_dependent"] = np.asarray(
        sim.calculate("is_tax_unit_dependent", year), dtype=bool
    )
    out["filing_status"] = sim.calculate("filing_status", year)
    out["state"] = np.asarray(sim.calculate("state_code", year, map_to="tax_unit"))
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    p = sim.tax_benefit_system.parameters(year)
    out["p"] = p.gov.irs.deductions.qbi
    out["mo_rate"] = p.gov.states.mo.tax.income.deductions.business_income.rate
    out["ia_fraction"] = (
        p.gov.states.ia.tax.income.deductions.qualified_business_income.fraction
    )
    return out


def _unit_sum(run, values):
    n = len(run["qualified_business_income_deduction"])
    return np.bincount(run["unit"], weights=values, minlength=n)


def _applicable_rate(run):
    p = run["p"]
    statuses = run["filing_status"]
    start = np.asarray(p.phase_out.start[statuses], dtype=float)
    length = np.asarray(p.phase_out.length[statuses], dtype=float)
    excess = np.maximum(0, run["taxable_income_less_qbid"] - start)
    reduction = np.divide(excess, length, out=np.ones_like(excess), where=length > 0)
    return 1 - np.minimum(1, reduction)


def _check(units, year):
    run = _run(units, year, zero_dependents=False)
    zeroed = _run(units, year, zero_dependents=True)
    filer = ~run["is_dependent"]
    deduction = run["qualified_business_income_deduction"]

    # 1. Dependents' business inputs never reach the filer's return.
    for name in TAX_UNIT_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )
    for name in PERSON_OUTPUTS:
        np.testing.assert_allclose(
            run[name][filer], zeroed[name][filer], atol=TOLERANCE, err_msg=name
        )

    # 2. Conservation.
    shares = run["qualified_business_income_deduction_person"]
    has_amounts = _unit_sum(run, filer * run["qbid_amount"]) > 0
    np.testing.assert_allclose(
        _unit_sum(run, shares)[has_amounts], deduction[has_amounts], atol=TOLERANCE
    )
    assert (shares[~filer] == 0).all()
    is_ia = run["state"] == "IA"
    if is_ia.any():
        np.testing.assert_allclose(
            _unit_sum(run, run["ia_qbi_deduction"])[is_ia & has_amounts],
            (run["ia_fraction"] * deduction)[is_ia & has_amounts],
            atol=TOLERANCE,
        )

    # 3. Differential against numpy over the head and spouse.
    p = run["p"]
    cap = p.max.rate * np.maximum(
        0, run["taxable_income_less_qbid"] - run["adjusted_net_capital_gain"]
    )
    pre_floor = np.minimum(_unit_sum(run, filer * run["qbid_amount"]), cap)
    reference = pre_floor
    if p.deduction_floor.in_effect:
        legacy = run["business_is_sstb"] > 0
        qbi = run["qualified_business_income"]
        non_sstb = np.where(legacy, 0, qbi)
        sstb = run["sstb_qualified_business_income"] + np.where(legacy, qbi, 0)
        eligible = non_sstb + sstb * _applicable_rate(run)[run["unit"]]
        floor = p.deduction_floor.amount.calc(_unit_sum(run, filer * eligible))
        reference = np.maximum(pre_floor, floor)
    np.testing.assert_allclose(deduction, reference, atol=TOLERANCE)
    is_mo = run["state"] == "MO"
    positive_qbi = np.maximum(
        0, run["qualified_business_income"] + run["sstb_qualified_business_income"]
    )
    np.testing.assert_allclose(
        run["mo_business_income_deduction"][is_mo],
        (run["mo_rate"] * _unit_sum(run, filer * positive_qbi))[is_mo],
        atol=TOLERANCE,
    )

    # 4. Bounds.
    assert (deduction >= -TOLERANCE).all()
    assert (pre_floor <= cap + TOLERANCE).all()
    all_members = np.minimum(_unit_sum(run, run["qbid_amount"]), cap)
    assert (pre_floor <= all_members + TOLERANCE).all()


# Each example is one vectorized batch of tax units, so a few examples cover
# many units; the seeded population runs once.
SETTINGS = dict(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_dependents_stay_off_the_filers_qbid_2026(units):
    # 2026 adds the 199A(i) minimum deduction and the wider phase-in range.
    _check(units, 2026)


def test_seeded_population_2025():
    _check(_seeded_units(), 2025)
