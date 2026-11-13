"""Ohio deductions and addbacks use income on the filers' return.

R.C. 5747.79(A)(1) permits qualifying capital gain only to the extent it
has not been excluded from federal or Ohio AGI; subsection (B) limits the
deduction to deductible payroll. A dependent's income is excluded from the
filers' federal AGI. R.C. 5747.01(A)(28) limits the business deduction to
business income in federal AGI, capped at $250,000 for single and joint
returns. Subsection (II) adds both deductions back to Ohio modified AGI.

Sources: https://codes.ohio.gov/ohio-revised-code/section-5747.79 and
https://codes.ohio.gov/ohio-revised-code/section-5747.01.

Each Hypothesis example evaluates six tax units and their twins together:
one or two filers and one through three dependent children. Actual capital gains and
S-corporation income avoid unrelated loss allocation. An independent sum
over filers checks federal AGI, the deductions and Ohio AGI, then a twin
tax unit with dependent gain and business inputs zeroed checks that those
inputs cannot change the filers' deductions or either Ohio AGI measure.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
TOLERANCE = 0.01
DEPENDENT_INPUTS = (
    "long_term_capital_gains",
    "s_corp_income",
    "oh_qualifying_capital_gain",
    "oh_qualifying_capital_gain_deductible_payroll",
)
PERSON_OUTPUTS = (
    "adjusted_gross_income_person",
    "oh_business_income_deduction_person",
    "oh_qualifying_capital_gain_deduction",
)
UNIT_OUTPUTS = (
    "adjusted_gross_income",
    "oh_business_income_deduction",
    "oh_agi",
    "oh_modified_agi",
)


@st.composite
def person_amounts(draw, *, dependent):
    return {
        "employment_income": draw(st.integers(1, 100_000)),
        "s_corp_income": draw(st.integers(1 if dependent else 0, 350_000)),
        "long_term_capital_gains": draw(st.integers(1 if dependent else 0, 400_000)),
        "oh_qualifying_capital_gain": draw(
            st.integers(1 if dependent else -50_000, 400_000)
        ),
        "oh_qualifying_capital_gain_deductible_payroll": draw(
            st.integers(1 if dependent else -50_000, 400_000)
        ),
    }


@st.composite
def tax_unit_batch(draw):
    return [
        {
            "filers": [draw(person_amounts(dependent=False)) for _ in range(n_filers)],
            "dependents": [
                draw(person_amounts(dependent=True)) for _ in range(n_dependents)
            ],
        }
        for n_filers in (1, 2)
        for n_dependents in (1, 2, 3)
    ]


def _run(units):
    situation = {
        "people": {},
        "tax_units": {},
        "households": {},
        "marital_units": {},
    }
    # Evaluate each unit and its twin in one vectorized simulation.
    for i, unit in enumerate(units + units):
        members, filers = [], []
        for j, amounts in enumerate(unit["filers"] + unit["dependents"]):
            dependent = j >= len(unit["filers"])
            name = f"person_{i}_{j}"
            values = {
                **amounts,
                "age": 10 if dependent else 45,
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1 and not dependent,
                "is_tax_unit_dependent": dependent,
            }
            if dependent and i >= len(units):
                values.update({variable: 0 for variable in DEPENDENT_INPUTS})
            situation["people"][name] = {
                variable: {YEAR: value} for variable, value in values.items()
            }
            members.append(name)
            if dependent:
                situation["marital_units"][name] = {"members": [name]}
            else:
                filers.append(name)
        situation["marital_units"][f"filers_{i}"] = {"members": filers}
        situation["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {YEAR: "JOINT" if len(filers) == 2 else "SINGLE"},
        }
        situation["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "OH"},
        }
    simulation = Simulation(situation=situation)
    outputs = {
        variable: np.asarray(simulation.calculate(variable, YEAR), dtype=float)
        for variable in PERSON_OUTPUTS + UNIT_OUTPUTS
    }
    outputs["dependent"] = np.asarray(
        simulation.calculate("is_tax_unit_dependent", YEAR), dtype=bool
    )
    index = simulation.populations["tax_unit"].members_entity_id
    n_people = len(index) // 2
    runs = []
    for half in (0, 1):
        results = {}
        for variable in PERSON_OUTPUTS + ("dependent",):
            results[variable] = outputs[variable][
                half * n_people : (half + 1) * n_people
            ]
        for variable in UNIT_OUTPUTS:
            results[variable] = outputs[variable][
                half * len(units) : (half + 1) * len(units)
            ]
        results["unit"] = index[half * n_people : (half + 1) * n_people] - half * len(
            units
        )
        runs.append(results)
    return runs


def _unit_sum(run, amounts):
    return np.bincount(
        run["unit"], weights=amounts, minlength=len(run["adjusted_gross_income"])
    )


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(tax_unit_batch())
def test_dependent_income_cannot_change_ohio_filer_deductions(units):
    run, zeroed = _run(units)
    filer = ~run["dependent"]
    people = [
        person for unit in units for person in unit["filers"] + unit["dependents"]
    ]

    def inputs(variable):
        return np.array([person[variable] for person in people], dtype=float)

    expected_person_agi = filer * (
        inputs("employment_income")
        + inputs("s_corp_income")
        + inputs("long_term_capital_gains")
    )
    expected_agi = _unit_sum(run, expected_person_agi)
    expected_business = np.minimum(
        250_000, _unit_sum(run, filer * inputs("s_corp_income"))
    )
    expected_capital_person = filer * np.minimum.reduce(
        [
            np.maximum(0, inputs("oh_qualifying_capital_gain")),
            inputs("long_term_capital_gains"),
            np.maximum(0, inputs("oh_qualifying_capital_gain_deductible_payroll")),
        ]
    )
    expected_capital = _unit_sum(run, expected_capital_person)

    for results in (run, zeroed):
        for variable in PERSON_OUTPUTS:
            np.testing.assert_array_equal(results[variable][run["dependent"]], 0)
        np.testing.assert_allclose(
            results["adjusted_gross_income_person"],
            expected_person_agi,
            atol=TOLERANCE,
        )
        np.testing.assert_allclose(
            results["adjusted_gross_income"], expected_agi, atol=TOLERANCE
        )
        np.testing.assert_allclose(
            results["oh_qualifying_capital_gain_deduction"],
            expected_capital_person,
            atol=TOLERANCE,
        )
        np.testing.assert_allclose(
            results["oh_business_income_deduction"],
            expected_business,
            atol=TOLERANCE,
        )
        np.testing.assert_allclose(
            _unit_sum(results, results["oh_business_income_deduction_person"]),
            expected_business,
            atol=TOLERANCE,
        )
        np.testing.assert_allclose(
            results["oh_agi"],
            expected_agi - expected_business - expected_capital,
            atol=TOLERANCE,
        )
        np.testing.assert_allclose(
            results["oh_modified_agi"], expected_agi, atol=TOLERANCE
        )
    for variable in UNIT_OUTPUTS:
        np.testing.assert_allclose(
            run[variable], zeroed[variable], atol=TOLERANCE, err_msg=variable
        )
    for variable in PERSON_OUTPUTS:
        np.testing.assert_allclose(
            run[variable][filer],
            zeroed[variable][filer],
            atol=TOLERANCE,
            err_msg=variable,
        )
