"""Invariants for a tax unit dependent's unemployment compensation in CA, RI and WI.

`irs_gross_income` leaves out every tax unit dependent's income, which the
dependent reports on their own return. California's Schedule CA subtraction
(section B line 7), Rhode Island's add-back of compensation excluded from
federal AGI (RIGL 44-30-12(b)(6)) and Wisconsin's unemployment compensation
worksheet (Schedule SB line 3, line 1 "from line 7 of federal Schedule 1")
all adjust the filers' own federal AGI, so a dependent's compensation must
not move them.

The tests draw a seeded random population of tax units, each single or
joint, with wages, unemployment compensation and state tax refunds for the
head and spouse, and zero to two dependent children with unemployment
compensation. Every unit is placed in each of the three states, and each
scenario runs as one vectorized simulation. TY2020 is the only year with a
federal exclusion (IRC 85(c)), so Rhode Island's add-back is non-zero only
then; TY2024 checks California and Wisconsin in a year without it. In 2020
each person's taxable compensation is an input (their compensation less a
drawn excluded part), so the properties check the state lines whatever the
federal exclusion calculation gives.

1. Each state line, and the state AGI built on it, is the same whether or
   not the dependents have unemployment compensation.
2. Each line equals a reference built from the head's and spouse's own
   amounts: California subtracts their taxable compensation and state tax
   refunds; Rhode Island adds their federally excluded compensation;
   Wisconsin runs its worksheet on their taxable compensation.
3. For tax units without dependents each line equals the sum over every
   member, as before.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

SEED = 20261012
TOLERANCE = 0.01  # dollars
STATES = ["CA", "RI", "WI"]
YEARS = [2020, 2024]
N_UNITS = 40
# Wisconsin's worksheet base (line 3) by filing status: $18,000 joint,
# $12,000 otherwise (2024 Schedule SB instructions, page 2). No unit here is
# married filing separately.
EXCLUSION_YEAR = 2020
EXCLUSION_CAP = 10_200
WI_BASE_JOINT = 18_000
WI_BASE_OTHER = 12_000
WI_RATE = 0.5


def _draw_units(n, rng):
    def draw(scale):
        return float(round(rng.choice([0.0, rng.uniform(0, scale)])))

    def excluded(compensation):
        # The part of 2020 compensation excluded from federal AGI: none, all
        # up to the cap, or part of it.
        share = float(rng.choice([0.0, 1.0, 0.5]))
        return float(round(min(compensation, EXCLUSION_CAP) * share))

    units = []
    for _ in range(n):
        joint = bool(rng.random() < 0.5)
        # Low wages in some units keep Wisconsin's worksheet in its
        # phase-out range, where line 7 is below twice the compensation.
        wage_scale = float(rng.choice([20_000, 90_000]))

        def filer():
            compensation = draw(15_000)
            return {
                "employment_income": draw(wage_scale),
                "unemployment_compensation": compensation,
                "salt_refund_income": draw(1_500),
                "excluded_2020": excluded(compensation),
            }

        def dependent():
            compensation = draw(12_000)
            return {
                "age": int(rng.integers(5, 19)),
                "unemployment_compensation": compensation,
                "excluded_2020": excluded(compensation),
            }

        units.append(
            {
                "joint": joint,
                "head": filer(),
                "spouse": filer() if joint else None,
                "dependents": [dependent() for _ in range(int(rng.integers(0, 3)))],
            }
        )
    return units


def _compensation_inputs(person, year, scale=1.0):
    compensation = scale * person["unemployment_compensation"]
    inputs = {"unemployment_compensation": {year: compensation}}
    if year == EXCLUSION_YEAR:
        taxable = compensation - scale * person["excluded_2020"]
        inputs["taxable_unemployment_compensation"] = {year: taxable}
    return inputs


def _filer_inputs(filer, state, year):
    # Only California subtracts state tax refunds among these lines;
    # Wisconsin's worksheet counts them on line 5, which the model leaves out,
    # so the refunds go only to the California units.
    refunds = filer["salt_refund_income"] if state == "CA" else 0.0
    return {
        "employment_income": {year: filer["employment_income"]},
        "salt_refund_income": {year: refunds},
        **_compensation_inputs(filer, year),
    }


def _situation(units, year, *, zero_dependents=False):
    people, tax_units, marital_units, spm_units = {}, {}, {}, {}
    families, households = {}, {}
    for state in STATES:
        for i, u in enumerate(units):
            key = f"{state}_{i}"
            head = f"head_{key}"
            members = [head]
            couple = [head]
            people[head] = {
                "age": {year: 40},
                "is_tax_unit_head": {year: True},
                "is_tax_unit_spouse": {year: False},
                "is_tax_unit_dependent": {year: False},
                **_filer_inputs(u["head"], state, year),
            }
            if u["spouse"] is not None:
                spouse = f"spouse_{key}"
                members.append(spouse)
                couple.append(spouse)
                people[spouse] = {
                    "age": {year: 38},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: True},
                    "is_tax_unit_dependent": {year: False},
                    **_filer_inputs(u["spouse"], state, year),
                }
            marital_units[f"mu_{key}"] = {"members": couple}
            for j, dependent in enumerate(u["dependents"]):
                child = f"child_{key}_{j}"
                members.append(child)
                marital_units[f"mu_{key}_{j}"] = {"members": [child]}
                people[child] = {
                    "age": {year: dependent["age"]},
                    "is_tax_unit_head": {year: False},
                    "is_tax_unit_spouse": {year: False},
                    "is_tax_unit_dependent": {year: True},
                    **_compensation_inputs(
                        dependent, year, scale=0.0 if zero_dependents else 1.0
                    ),
                }
            tax_units[f"tu_{key}"] = {"members": members}
            spm_units[f"spm_{key}"] = {"members": members}
            families[f"fam_{key}"] = {"members": members}
            households[f"hh_{key}"] = {
                "members": members,
                "state_name": {year: state},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def _state_slice(state):
    start = STATES.index(state) * N_UNITS
    return slice(start, start + N_UNITS)


def _filer_sum(sim, variable, year):
    """Sum a person-level variable over each tax unit's head and spouse."""
    values = sim.calculate(variable, year)
    filer = ~sim.calculate("is_tax_unit_dependent", year)
    tax_unit = sim.populations["tax_unit"]
    return tax_unit.sum(values * filer)


def _member_sum(sim, variable, year):
    values = sim.calculate(variable, year)
    return sim.populations["tax_unit"].sum(values)


LINES = {
    "CA": ("ca_agi_subtractions", "ca_agi"),
    "RI": ("ri_additions", "ri_agi"),
    "WI": ("wi_unemployment_compensation_subtraction", "wi_agi"),
}


@pytest.fixture(scope="module", params=YEARS)
def simulations(request):
    year = request.param
    rng = np.random.default_rng(SEED + year)
    units = _draw_units(N_UNITS, rng)
    with_income = Simulation(situation=_situation(units, year))
    without_income = Simulation(situation=_situation(units, year, zero_dependents=True))
    return year, units, with_income, without_income


def test_dependents_compensation_leaves_state_lines_unchanged(simulations):
    year, units, with_income, without_income = simulations
    # The population must exercise the property: some dependents have
    # compensation in every state.
    assert any(d["unemployment_compensation"] for u in units for d in u["dependents"])
    for state, variables in LINES.items():
        rows = _state_slice(state)
        for variable in variables:
            np.testing.assert_allclose(
                with_income.calculate(variable, year)[rows],
                without_income.calculate(variable, year)[rows],
                atol=TOLERANCE,
                err_msg=f"{state} {variable} {year}",
            )


def test_state_lines_use_the_filers_own_amounts(simulations):
    year, units, sim, _ = simulations
    filer_taxable = _filer_sum(sim, "taxable_unemployment_compensation", year)
    filer_excluded = _filer_sum(sim, "tax_exempt_unemployment_compensation", year)
    filer_refunds = _filer_sum(sim, "salt_refund_income", year)

    ca = _state_slice("CA")
    np.testing.assert_allclose(
        sim.calculate("ca_agi_subtractions", year)[ca],
        (filer_taxable + filer_refunds)[ca],
        atol=TOLERANCE,
    )

    ri = _state_slice("RI")
    np.testing.assert_allclose(
        sim.calculate("ri_additions", year)[ri],
        filer_excluded[ri],
        atol=TOLERANCE,
    )
    if year == 2020:
        # The units draw enough compensation that the 2020 exclusion bites.
        assert filer_excluded[ri].sum() > 0

    wi = _state_slice("WI")
    joint = np.array([u["joint"] for u in units])
    base = np.where(joint, WI_BASE_JOINT, WI_BASE_OTHER)
    agi = sim.calculate("adjusted_gross_income", year)[wi]
    taxable_social_security = sim.calculate("tax_unit_taxable_social_security", year)[
        wi
    ]
    line_1 = filer_taxable[wi]
    line_8 = np.maximum(0, agi - base - taxable_social_security) * WI_RATE
    expected = line_1 - np.minimum(line_1, line_8)
    np.testing.assert_allclose(
        sim.calculate("wi_unemployment_compensation_subtraction", year)[wi],
        expected,
        atol=TOLERANCE,
    )
    # Some units fall in the phase-out range, where the worksheet keeps part
    # of the compensation taxable.
    assert ((expected > 0) & (expected < line_1)).any()


def test_units_without_dependents_match_the_sum_over_members(simulations):
    year, units, sim, _ = simulations
    no_dependents = np.array([not u["dependents"] for u in units])
    ca = _state_slice("CA")
    member_ca = (
        _member_sum(sim, "taxable_unemployment_compensation", year)
        + _member_sum(sim, "salt_refund_income", year)
    )[ca]
    np.testing.assert_allclose(
        sim.calculate("ca_agi_subtractions", year)[ca][no_dependents],
        member_ca[no_dependents],
        atol=TOLERANCE,
    )
    ri = _state_slice("RI")
    member_ri = _member_sum(sim, "tax_exempt_unemployment_compensation", year)[ri]
    np.testing.assert_allclose(
        sim.calculate("ri_additions", year)[ri][no_dependents],
        member_ri[no_dependents],
        atol=TOLERANCE,
    )
