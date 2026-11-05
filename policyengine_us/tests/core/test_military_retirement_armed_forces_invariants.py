"""Armed forces pay reaches state rules through one input, and Rhode Island tests age per person.

Each year uses one vectorized simulation. Every drawn tax unit appears in five
states, once with the default input and once with its pay marked as NOAA or
Public Health Service pay. The copies share every other input. Ages span the
state age tests, amounts span the deduction caps, and some units hold a dependent
with pay of their own.
"""

import numpy as np
import pytest

from policyengine_us import Simulation


SEED = 20261105
TOLERANCE = 0.05  # dollars; model calculations use float32 arrays
YEARS = [2022, 2024, 2025, 2026]
STATES = ["IN", "ND", "NM", "RI", "SC"]
FILER_AGES = [40, 55, 60, 64, 65, 66, 67, 70, 75, 85]
UNIT_COUNT = 24
GROUPS = ("people", "tax_units", "marital_units", "households", "families", "spm_units")


def _draw_units(year):
    rng = np.random.default_rng(SEED + year)

    def filer(i, age, surviving=False):
        return {
            "age": age,
            "taxable_private_pension_income": (
                0.0 if i % 5 == 0 else float(rng.integers(1, 40_001))
            ),
            "military_retirement_pay": (
                0.0 if i % 7 == 0 else float(rng.integers(1, 40_001))
            ),
            "military_retirement_pay_survivors": (
                float(rng.integers(1, 30_001)) if surviving else 0.0
            ),
            "is_surviving_spouse": surviving,
            "deceased_spouse_age": 70 if surviving else 0,
        }

    units = []
    for i in range(UNIT_COUNT):
        joint = i % 2 == 1
        units.append(
            {
                "head": filer(
                    i,
                    FILER_AGES[i % len(FILER_AGES)],
                    surviving=not joint and i % 4 == 0,
                ),
                "spouse": (
                    filer(i, FILER_AGES[(i + 4) % len(FILER_AGES)]) if joint else None
                ),
                "dependent": (
                    {
                        "age": 70,
                        "taxable_private_pension_income": 0.0,
                        "military_retirement_pay": float(rng.integers(1, 20_001)),
                        "military_retirement_pay_survivors": 0.0,
                        "is_surviving_spouse": False,
                        "deceased_spouse_age": 0,
                    }
                    if i % 6 == 2
                    else None
                ),
            }
        )
    return units


def _situation(units, year):
    groups = {name: {} for name in GROUPS}
    people, tax_units = [], []

    def add_person(role, key, record, state, noaa, unit_row):
        name = f"{role}_{key}"
        person = {variable: {year: value} for variable, value in record.items()}
        person.update(
            {
                "is_tax_unit_head": {year: role == "head"},
                "is_tax_unit_spouse": {year: role == "spouse"},
                "is_tax_unit_dependent": {year: role == "dependent"},
            }
        )
        if noaa:
            person["military_retirement_pay_is_armed_forces"] = {year: False}
        groups["people"][name] = person
        people.append(
            {
                "state": state,
                "noaa": noaa,
                "filer": role != "dependent",
                "unit": unit_row,
                "age": record["age"],
                "pension": record["taxable_private_pension_income"],
                "pay": record["military_retirement_pay"],
                "survivors": record["military_retirement_pay_survivors"],
                "surviving": record["is_surviving_spouse"],
                "deceased_age": record["deceased_spouse_age"],
            }
        )
        return name

    for state in STATES:
        for noaa in (False, True):
            for i, unit in enumerate(units):
                key = f"{state}_{int(noaa)}_{i}"
                unit_row = len(tax_units)
                tax_units.append({"state": state, "noaa": noaa})
                couple = [add_person("head", key, unit["head"], state, noaa, unit_row)]
                if unit["spouse"] is not None:
                    couple.append(
                        add_person("spouse", key, unit["spouse"], state, noaa, unit_row)
                    )
                members = list(couple)
                groups["marital_units"][f"couple_{key}"] = {"members": couple}
                if unit["dependent"] is not None:
                    name = add_person(
                        "dependent", key, unit["dependent"], state, noaa, unit_row
                    )
                    members.append(name)
                    groups["marital_units"][f"dependent_{key}"] = {"members": [name]}
                groups["tax_units"][f"tax_unit_{key}"] = {"members": members}
                groups["households"][f"household_{key}"] = {
                    "members": members,
                    "state_name": {year: state},
                }
                groups["families"][f"family_{key}"] = {"members": members}
                groups["spm_units"][f"spm_unit_{key}"] = {"members": members}

    def columns(rows):
        return {name: np.array([row[name] for row in rows]) for name in rows[0]}

    return groups, columns(people), columns(tax_units)


class Run:
    def __init__(self, year):
        self.year = year
        situation, self.people, self.tax_units = _situation(_draw_units(year), year)
        self.sim = Simulation(situation=situation)
        self.states = self.sim.tax_benefit_system.parameters(year).gov.states

    def calc(self, variable):
        return np.asarray(self.sim.calculate(variable, self.year), dtype=float)

    def by_unit(self, amounts):
        return np.bincount(
            self.people["unit"], weights=amounts, minlength=len(self.tax_units["noaa"])
        )


@pytest.fixture(scope="module", params=YEARS)
def run(request):
    return Run(request.param)


def _assert_close(actual, expected, message):
    np.testing.assert_allclose(
        actual, expected, rtol=0, atol=TOLERANCE, err_msg=message
    )


def test_the_default_input_counts_all_pay_as_armed_forces_pay(run):
    people = run.people
    armed = ~people["noaa"]
    _assert_close(
        run.calc("armed_forces_retirement_pay"),
        people["pay"] * armed,
        "armed_forces_retirement_pay",
    )
    _assert_close(
        run.calc("armed_forces_retirement_pay_survivors"),
        people["survivors"] * armed,
        "armed_forces_retirement_pay_survivors",
    )


@pytest.mark.parametrize(
    "state, variable, start",
    [
        ("ND", "nd_military_retirement_subtraction", 2019),
        ("RI", "ri_military_retirement_subtraction", 2023),
    ],
)
def test_military_subtractions_read_armed_forces_pay_only(run, state, variable, start):
    people = run.people
    rows = people["state"] == state
    amount = people["pay"] + people["survivors"] * people["surviving"]
    expected = amount * ~people["noaa"] * (run.year >= start)
    _assert_close(run.calc(variable)[rows], expected[rows], variable)


def test_new_mexico_exempts_armed_forces_pay_only(run):
    people = run.people
    p = run.states.nm.tax.income.exemptions.armed_forces_retirement_pay
    rows = people["state"] == "NM"
    amount = people["pay"] + people["survivors"] * people["surviving"] * (
        p.survivors_eligible
    )
    expected = np.minimum(amount, p.cap) * people["filer"] * ~people["noaa"]
    _assert_close(
        run.calc("nm_armed_forces_retirement_pay_exemption_person")[rows],
        expected[rows],
        "nm_armed_forces_retirement_pay_exemption_person",
    )


def test_indiana_covers_all_uniformed_services_from_2025(run):
    units = run.tax_units
    deduction = run.calc("in_military_retirement_deduction")
    indiana = units["state"] == "IN"
    armed = deduction[indiana & ~units["noaa"]]
    noaa = deduction[indiana & units["noaa"]]
    assert (armed > 0).any()
    _assert_close(noaa, armed if run.year >= 2025 else 0 * armed, "Indiana")


def test_south_carolina_takes_each_dollar_of_pay_on_one_line(run):
    people = run.people
    p = run.states.sc.tax.income.subtractions.retirement
    rows = people["state"] == "SC"
    armed = ~people["noaa"]
    pay, pension = people["pay"], people["pension"]
    cap = p.cap.calc(people["age"])

    military = run.calc("sc_military_deduction_indv")
    retirement = run.calc("sc_retirement_deduction_indv")
    expected_military = pay * armed * people["filer"]
    expected_retirement = people["filer"] * np.where(
        armed,
        np.minimum(np.maximum(cap - pay, 0), pension),
        np.minimum(cap, pension + pay),
    )
    _assert_close(military[rows], expected_military[rows], "12-6-1171 deduction")
    _assert_close(retirement[rows], expected_retirement[rows], "12-6-1170 deduction")

    # Armed forces status never lowers what a person deducts, and it changes
    # the total only when the pay exceeds the 12-6-1170 cap.
    total = military + retirement
    armed_total = total[rows & armed]
    noaa_total = total[rows & ~armed]
    assert (armed_total >= noaa_total - TOLERANCE).all()
    within_cap = (pay <= cap)[rows & armed]
    _assert_close(armed_total[within_cap], noaa_total[within_cap], "within the cap")
    assert (armed_total > noaa_total + TOLERANCE).any()


def test_south_carolina_takes_each_dollar_of_survivor_pay_on_one_line(run):
    people = run.people
    p = run.states.sc.tax.income.subtractions.retirement
    rows = people["state"] == "SC"
    armed = ~people["noaa"]
    survivors = people["survivors"] * people["surviving"] * people["filer"]
    cap = p.cap.calc(people["deceased_age"])
    assert (survivors[rows] > 0).any()
    _assert_close(
        run.calc("sc_military_deduction_survivors")[rows],
        (survivors * armed)[rows],
        "12-6-1171 survivor deduction",
    )
    _assert_close(
        run.calc("sc_retirement_deduction_survivors")[rows],
        (np.minimum(survivors, cap) * ~armed)[rows],
        "12-6-1170 survivor deduction",
    )


def test_rhode_island_tests_age_for_each_person(run):
    people = run.people
    p = run.states.ri.tax.income.agi.subtractions.taxable_retirement_income
    rows = run.tax_units["state"] == "RI"
    income = sum(run.calc(source) for source in p.sources)
    military = run.calc("ri_military_retirement_subtraction")
    capped = np.minimum(np.maximum(income - military, 0), p.cap) * people["filer"]
    qualifies = run.year - people["age"] <= p.birth_year
    eligible = run.calc("ri_retirement_income_subtraction_eligible")
    subtraction = run.calc("ri_retirement_income_subtraction")

    expected = run.by_unit(capped * qualifies) * eligible
    _assert_close(subtraction[rows], expected[rows], "Rhode Island per-person test")
    assert (subtraction[rows] <= run.by_unit(capped)[rows] + TOLERANCE).all()

    # The draws include eligible couples with a spouse too young to qualify.
    assert (rows & (eligible > 0) & (run.by_unit(capped * ~qualifies) > 0)).any()


def test_armed_forces_status_never_lowers_rhode_island_subtractions(run):
    people = run.people
    units = run.tax_units
    rows = units["state"] == "RI"
    military = run.by_unit(
        run.calc("ri_military_retirement_subtraction") * people["filer"]
    )
    total = military + run.calc("ri_retirement_income_subtraction")
    assert (
        total[rows & ~units["noaa"]] >= total[rows & units["noaa"]] - TOLERANCE
    ).all()
