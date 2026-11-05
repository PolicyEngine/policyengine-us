"""Reforms that pay a benefit add it to the baseline benefit lists.

The Texas rebate, the End Child Poverty Act, its Economic Dignity for All
Agenda version and the BOOST Act credit each pay a benefit, and each replaced
spm_unit_benefits with its own copy of the program list. The copies fell behind
the baseline, and every program a copy missed dropped out of SPM resources for
every household the reform applied to (#10226):

- Texas missed 19 state SSI supplements, and the three Tlaib copies missed 42
  supplements, Washington's cash programs (wa_sfa, wa_rca) and the Washington
  and West Virginia child care subsidies.
- The Tlaib copies listed acp and ebb, which spm_unit_net_income also adds, so
  ACP and EBB counted twice in SPM resources.
- The ECPA and BOOST copies of household_benefits missed CSFP and
  household_health_benefits.

Each reform now adds its own variables to the gov.household lists that the
baseline aggregates read, through add_to_list_parameter. These invariants hold
for every input:

1. add_to_list_parameter keeps every dated value of a list and its members in
   order, appends only the names a value lacks, and changes nothing when it
   runs again.
2. Under each reform, each benefit list in each year is the baseline list,
   followed by the reform's own additions and nothing else.
3. Applying a reform a second time changes no list. A simulation can apply a
   structural reform twice: once when its system is built, once at start.
4. For any household, spm_unit_benefits and household_benefits equal the sum
   of the baseline list's programs and the reform's own additions, each as the
   simulation computes it; spm_unit_benefits also adds the SPM's capped housing
   subsidy. A program that a copy drops, or that it counts twice, breaks the
   sum.
5. A dollar of ACP or EBB adds a dollar to spm_unit_net_income, under current
   law and under each reform.
"""

import gc

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import instant

from policyengine_us import Simulation
from policyengine_us.reforms.congress.tlaib.boost.boost_middle_class_tax_credit import (
    boost_middle_class_tax_credit,
)
from policyengine_us.reforms.congress.tlaib.economic_dignity_for_all_agenda.edaa_end_child_poverty_act import (
    end_child_poverty_act as edaa_end_child_poverty_act,
)
from policyengine_us.reforms.congress.tlaib.end_child_poverty_act import (
    end_child_poverty_act,
)
from policyengine_us.reforms.states.tx.rebate.tx_rebate import tx_rebate
from policyengine_us.system import CountryTaxBenefitSystem, system
from policyengine_us.tools.parameters import add_to_list_parameter

STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()

LISTS = ("spm_unit_benefits", "household_benefits", "household_state_benefits")

# The structural reforms that pay a benefit, and the variable each adds to the
# household and SPM benefit lists.
REFORMS = {
    "tx_rebate": (tx_rebate, "tx_rebate"),
    "end_child_poverty_act": (end_child_poverty_act, "ecpa_child_benefit"),
    "edaa_end_child_poverty_act": (edaa_end_child_poverty_act, "ecpa_child_benefit"),
    "boost_middle_class_tax_credit": (
        boost_middle_class_tax_credit,
        "boost_middle_class_tax_credit_paid_through_ssa",
    ),
}
OWN_BENEFITS = sorted({benefit for _, benefit in REFORMS.values()})

# What the spm_unit_benefits formula adds to its parameter list under current
# law. The housing subsidy stays out of the parameter so that no other
# aggregate reads an SPM valuation cap.
SPM_FORMULA_BENEFITS = ["spm_unit_capped_housing_subsidy"]


def additions(name, list_name, year):
    """The variables a reform adds to a benefit list in a year."""
    if name == "baseline":
        return []
    own = REFORMS[name][1]
    if name == "tx_rebate":
        # A state benefit: household_benefits reads it through
        # household_state_benefits, which carries it in 2027, its paid year.
        if list_name == "spm_unit_benefits":
            return [own]
        if list_name == "household_state_benefits" and year == 2027:
            return [own]
        return []
    if list_name == "household_state_benefits":
        return []
    return [own]


def benefit_list(tax_benefit_system, list_name, year):
    """A benefit list as formulas read it in a year.

    Reading the one parameter, not parameters(year), keeps the test from
    building and caching the whole parameter tree for every year it draws.
    """
    parameter = getattr(tax_benefit_system.parameters.gov.household, list_name)
    return list(parameter(f"{year}-01-01"))


# --- 1. add_to_list_parameter --------------------------------------------

NAMES = st.sampled_from("abcdefgh")


@st.composite
def dated_lists(draw):
    """A list parameter's dated values: {date: members}."""
    years = draw(st.lists(st.integers(2000, 2040), min_size=1, max_size=4, unique=True))
    return {
        f"{year}-01-01": draw(st.lists(NAMES, max_size=5, unique=True))
        for year in sorted(years)
    }


def list_parameter(values):
    node = ParameterNode(
        "root", data={"members": {"values": values, "metadata": {"unit": "list"}}}
    )
    return node.members


def value_on(values, date):
    """The members a dated list holds on a date, or None before its first."""
    starts = [start for start in sorted(values) if start <= date]
    return values[starts[-1]] if starts else None


@settings(max_examples=200, deadline=None)
@given(
    values=dated_lists(),
    names=st.lists(NAMES, min_size=1, max_size=4),
    dates=st.lists(st.integers(1999, 2042), min_size=1, max_size=6),
)
def test_add_to_list_parameter_appends_only_missing_names(values, names, dates):
    parameter = list_parameter(values)
    add_to_list_parameter(parameter, names)

    unique_names = list(dict.fromkeys(names))
    expected = {
        start: members + [name for name in unique_names if name not in members]
        for start, members in values.items()
    }
    starts = sorted(value.instant_str for value in parameter.values_list)
    assert starts == sorted(values)
    for year in dates:
        date = f"{year}-07-01"
        assert parameter(instant(date)) == value_on(expected, date)

    add_to_list_parameter(parameter, names)
    for year in dates:
        date = f"{year}-07-01"
        assert parameter(instant(date)) == value_on(expected, date)


def test_add_to_list_parameter_keeps_dates_from_year_zero():
    parameter = list_parameter({"0000-01-01": ["a"], "2026-01-01": ["a", "b"]})
    add_to_list_parameter(parameter, ["c", "b"])
    assert parameter(instant("1990-01-01")) == ["a", "c", "b"]
    assert parameter(instant("2025-12-31")) == ["a", "c", "b"]
    assert parameter(instant("2026-01-01")) == ["a", "b", "c"]


# --- 2 to 5. The reforms ---------------------------------------------------


@pytest.fixture(scope="module", params=["baseline", *REFORMS])
def policy(request):
    """(name, system): one reformed system at a time, each about 0.7 GB."""
    gc.collect()
    name = request.param
    if name == "baseline":
        yield name, system
        return
    reformed = CountryTaxBenefitSystem(reform=REFORMS[name][0])
    yield name, reformed
    del reformed
    gc.collect()


@settings(max_examples=60, deadline=None)
@given(year=st.integers(2015, 2035), list_name=st.sampled_from(LISTS))
def test_reform_lists_are_baseline_lists_plus_own_additions(policy, year, list_name):
    name, reformed = policy
    assert benefit_list(reformed, list_name, year) == (
        benefit_list(system, list_name, year) + additions(name, list_name, year)
    )


def test_applying_a_reform_twice_changes_no_list(policy):
    name, reformed = policy
    if name == "baseline":
        pytest.skip("current law applies no reform")
    twice = REFORMS[name][0](reformed)
    for year in (2015, 2023, 2026, 2027, 2028, 2035):
        for list_name in LISTS:
            assert benefit_list(twice, list_name, year) == benefit_list(
                reformed, list_name, year
            )


def program_state(program):
    """The state whose program this is, from its prefix, or None if national."""
    prefix = program.split("_")[0].upper()
    return prefix if len(prefix) == 2 and prefix in STATES else None


@st.composite
def households(draw):
    """(state, year, {program: amount}) for a one-person household.

    The programs are drawn from the baseline SPM list, what its formula adds,
    the reforms' own benefits and the broadband subsidies, which no benefit
    list may hold.
    """
    year = draw(st.integers(2023, 2027))
    state = draw(st.sampled_from(STATES))
    candidates = [
        program
        for program in benefit_list(system, "spm_unit_benefits", year)
        if program_state(program) in (None, state)
    ] + [*SPM_FORMULA_BENEFITS, *OWN_BENEFITS, "acp", "ebb"]
    programs = draw(st.lists(st.sampled_from(candidates), max_size=8, unique=True))
    amounts = st.integers(1, 30_000)
    return state, year, {program: draw(amounts) for program in programs}


def one_person(tax_benefit_system, state, year, earnings, inputs):
    """A one-person household, each input on its variable's entity."""
    groups = {"person": {}, "tax_unit": {}, "spm_unit": {}, "household": {}}
    for name, value in inputs.items():
        if name in tax_benefit_system.variables:
            entity = tax_benefit_system.variables[name].entity.key
            groups[entity][name] = {year: value}
    groups["person"].update(age={year: 40}, employment_income={year: earnings})
    groups["household"]["state_name"] = {year: state}
    members = ["you"]
    return {
        "people": {"you": groups["person"]},
        "tax_units": {"tax_unit": {"members": members, **groups["tax_unit"]}},
        "spm_units": {"spm_unit": {"members": members, **groups["spm_unit"]}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, **groups["household"]}},
    }


def summed(simulation, names, year):
    return sum(
        float(simulation.calculate(name, year, map_to="spm_unit").sum())
        for name in names
    )


# Totals run in float32, so allow for rounding; a dropped or repeated program
# moves a total by at least the $1 of its smallest amount.
ROUNDING = 0.5


@settings(max_examples=25, deadline=None)
@given(household=households())
# Programs the old reform copies dropped, and the broadband subsidies the Tlaib
# copies counted twice.
@example(household=("WY", 2027, {"wy_ssp": 240, "tx_rebate": 1_500}))
@example(household=("WA", 2026, {"wa_sfa": 1_000, "wa_rca": 500, "wa_ssp": 300}))
@example(household=("NY", 2024, {"ny_ssp": 1_052, "acp": 360, "ebb": 120}))
@example(household=("CA", 2026, {"ca_state_supplement": 2_000, "ssi": 4_000}))
def test_benefit_totals_sum_the_baseline_lists_and_own_additions(policy, household):
    name, reformed = policy
    state, year, inputs = household
    simulation = Simulation(
        tax_benefit_system=reformed,
        situation=one_person(reformed, state, year, 500_000, inputs),
    )

    spm_programs = (
        benefit_list(system, "spm_unit_benefits", year)
        + additions(name, "spm_unit_benefits", year)
        + SPM_FORMULA_BENEFITS
    )
    assert float(simulation.calculate("spm_unit_benefits", year).sum()) == (
        pytest.approx(summed(simulation, spm_programs, year), abs=ROUNDING)
    )

    household_programs = benefit_list(system, "household_benefits", year) + (
        additions(name, "household_benefits", year)
    )
    assert float(simulation.calculate("household_benefits", year).sum()) == (
        pytest.approx(summed(simulation, household_programs, year), abs=ROUNDING)
    )


@settings(max_examples=8, deadline=None)
@given(
    program=st.sampled_from(["acp", "ebb"]),
    amount=st.integers(1, 5_000),
    year=st.integers(2022, 2024),
    state=st.sampled_from(STATES),
)
def test_broadband_subsidies_reach_spm_net_income_once(
    policy, program, amount, year, state
):
    name, reformed = policy

    def net_income(value):
        simulation = Simulation(
            tax_benefit_system=reformed,
            situation=one_person(reformed, state, year, 100_000, {program: value}),
        )
        return float(simulation.calculate("spm_unit_net_income", year).sum())

    assert net_income(amount) - net_income(0) == pytest.approx(amount, abs=0.05)
