"""Property tests: a dependent's capital income stays off the filers' North
Dakota and Vermont returns.

Federal adjusted gross income leaves out a tax unit dependent's income
(irs_gross_income), which the dependent reports on their own return (2025
Form 8814, line 4; the model does not implement the Form 8814 election). Both
states start from the filers' federal return:

- N.D.C.C. 57-38-30.3(2) defines North Dakota taxable income as "the federal
  taxable income of an individual", reduced by 40% of "the taxpayer's net
  long-term capital gain" ((d)(1); Form ND-1 line 6, from the filer's
  Schedule D lines 15 and 16, "If zero or less ... no exclusion is allowed")
  and of qualified dividends ((d)(2); Form ND-1 line 13, from Form 1040 line
  3a), and by interest on U.S. obligations ((a)).
- 32 V.S.A. 5811(21) defines Vermont taxable income as the individual's
  federal adjusted gross income, increased by interest on non-Vermont state
  and local obligations ((A)(i)) and decreased, "to the extent such income is
  included in federal adjusted gross income", by interest on U.S. government
  obligations ((B)(i)) and by 40% of gains on "assets held by the taxpayer for
  more than three years" ((B)(ii)).

So for every tax unit in either state, and any capital income its dependents
have (qualified and other dividends, long- and short-term gains and losses,
capital gain distributions, taxable, tax-exempt and U.S. government interest,
and Vermont-eligible long-term gains):

1. nd_income_tax and vt_income_tax are the same as when the dependents have
   none. So are federal adjusted gross income and taxable income, the base
   both states start from.
2. nd_qdiv_subtraction is 40% of the filers' qualified dividends, and
   nd_ltcg_subtraction is 40% of max(0, min(line 15, line 16)) of the filers'
   own Schedule D, with capital gain distributions on line 15.
3. vt_percentage_capital_gains_exclusion is 40% of the filers' eligible gains,
   up to the cap, vt_additions is the filers' tax-exempt interest, and
   us_govt_interest is the filers' U.S. government interest.

Two restrictions keep effects that are outside this check out of the draws:

- The filers earn at least $80,000, so no earned income tax credit is at
  stake. Vermont's is a share of the federal credit, whose investment income
  test (eitc_relevant_investment_income) is not changed here.
- Vermont filers have at least $50,000 of their own long-term gain and no
  short-term loss, and Vermont dependents have gains, not losses. Until
  PolicyEngine/policyengine-us#9855 is merged, the $5,000 flat part of
  vt_capital_gains_exclusion reads the federal adjusted net capital gain,
  which on main still counts a dependent's gains and losses. With these
  amounts the flat part is at its cap either way.

Amounts are whole dollars of at most $400,000, so every sum is exact in single
precision and twins are compared to the cent.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01

# Each person's capital income inputs.
CAPITAL_INPUTS = [
    "qualified_dividend_income",
    "non_qualified_dividend_income",
    "long_term_capital_gains",
    "short_term_capital_gains",
    "non_sch_d_capital_gains",
    "taxable_interest_income",
    "us_govt_interest_person",
    "tax_exempt_interest_income",
    "long_term_capital_gains_on_assets_eligible_for_vt_exclusion",
]
SAME_AS_WITHOUT_DEPENDENT_INCOME = [
    "adjusted_gross_income",
    "taxable_income",
    "nd_income_tax",
    "vt_income_tax",
]
UNIT_OUTPUTS = SAME_AS_WITHOUT_DEPENDENT_INCOME + [
    "nd_qdiv_subtraction",
    "nd_ltcg_subtraction",
    "vt_percentage_capital_gains_exclusion",
    "vt_additions",
    "us_govt_interest",
]


def amount(low, high):
    return st.integers(low, high).map(float)


@st.composite
def capital_income(draw, vermont, filer):
    """One person's capital income. U.S. government interest is part of
    taxable interest, and Vermont-eligible gains are part of long-term
    gains."""
    if vermont and filer:
        long_term = draw(amount(50_000, 300_000))
        short_term = draw(amount(0, 20_000))
    elif vermont:
        long_term = draw(amount(0, 300_000))
        short_term = draw(amount(0, 50_000))
    else:
        long_term = draw(amount(-30_000, 300_000))
        short_term = draw(amount(-20_000, 50_000))
    taxable_interest = draw(amount(0, 50_000))
    return {
        "qualified_dividend_income": draw(amount(0, 50_000)),
        "non_qualified_dividend_income": draw(amount(0, 20_000)),
        "long_term_capital_gains": long_term,
        "short_term_capital_gains": short_term,
        "non_sch_d_capital_gains": draw(amount(0, 20_000)),
        "taxable_interest_income": taxable_interest,
        "us_govt_interest_person": draw(amount(0, int(taxable_interest))),
        "tax_exempt_interest_income": draw(amount(0, 50_000)),
        "long_term_capital_gains_on_assets_eligible_for_vt_exclusion": (
            draw(amount(0, int(long_term))) if long_term > 0 else 0.0
        ),
    }


@st.composite
def tax_units(draw):
    state = draw(st.sampled_from(["ND", "VT"]))
    vermont = state == "VT"
    n_filers = draw(st.integers(1, 2))
    filers = [
        {
            "age": draw(st.integers(30, 64)),
            "employment_income": draw(amount(80_000, 400_000)) if i == 0 else 0.0,
            **draw(capital_income(vermont, filer=True)),
        }
        for i in range(n_filers)
    ]
    dependents = [
        {
            "age": draw(st.integers(1, 17)),
            **draw(capital_income(vermont, filer=False)),
        }
        for _ in range(draw(st.integers(1, 2)))
    ]
    return {"state": state, "filers": filers, "dependents": dependents}


def without_dependent_income(unit):
    zero = {name: 0.0 for name in CAPITAL_INPUTS}
    return {**unit, "dependents": [{**d, **zero} for d in unit["dependents"]]}


def build_situation(units):
    """One tax unit per household: the head, an optional spouse and the
    dependents, each dependent in a marital unit of their own."""
    people, tax_units_out, marital_units, households = {}, {}, {}, {}
    for i, unit in enumerate(units):
        members = []
        for j, person in enumerate(unit["filers"] + unit["dependents"]):
            name = f"person_{i}_{j}"
            filer = j < len(unit["filers"])
            people[name] = {
                "is_tax_unit_head": {YEAR: j == 0},
                "is_tax_unit_spouse": {YEAR: j == 1 and filer},
                "is_tax_unit_dependent": {YEAR: not filer},
                **{key: {YEAR: value} for key, value in person.items()},
            }
            members.append(name)
            if not filer:
                marital_units[f"dependent_{i}_{j}"] = {"members": [name]}
        tax_units_out[f"tax_unit_{i}"] = {"members": members}
        marital_units[f"filers_{i}"] = {"members": members[: len(unit["filers"])]}
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: unit["state"]},
        }
    return {
        "people": people,
        "tax_units": tax_units_out,
        "marital_units": marital_units,
        "households": households,
    }


def calculate(units):
    simulation = Simulation(situation=build_situation(units))
    results = {
        variable: np.asarray(simulation.calculate(variable, YEAR))
        for variable in UNIT_OUTPUTS
    }
    p = simulation.tax_benefit_system.parameters(YEAR).gov.states
    return results, p


def filer_total(unit, name):
    return sum(person[name] for person in unit["filers"])


def check(units):
    twins = [without_dependent_income(unit) for unit in units]
    results, p = calculate(units + twins)
    n = len(units)

    # 1. The same taxes and federal base as without the dependents' income.
    for variable in SAME_AS_WITHOUT_DEPENDENT_INCOME:
        np.testing.assert_allclose(
            results[variable][:n],
            results[variable][n:],
            atol=TOLERANCE,
            err_msg=variable,
        )

    nd = p.nd.tax.income.taxable_income.subtractions
    vt = p.vt.tax.income.agi.exclusions.capital_gain.percentage
    is_nd = np.array([unit["state"] == "ND" for unit in units])
    is_vt = ~is_nd
    long_term = np.array(
        [
            filer_total(u, "long_term_capital_gains")
            + filer_total(u, "non_sch_d_capital_gains")
            for u in units
        ]
    )
    short_term = np.array([filer_total(u, "short_term_capital_gains") for u in units])
    reference = {
        # 2. North Dakota, from the filers' own amounts.
        "nd_qdiv_subtraction": nd.qdiv_fraction
        * np.array([filer_total(u, "qualified_dividend_income") for u in units]),
        "nd_ltcg_subtraction": nd.ltcg_fraction
        * np.maximum(0, np.minimum(long_term, long_term + short_term)),
        # 3. Vermont, from the filers' own amounts.
        "vt_percentage_capital_gains_exclusion": np.minimum(
            vt.rate
            * np.array(
                [
                    filer_total(
                        u, "long_term_capital_gains_on_assets_eligible_for_vt_exclusion"
                    )
                    for u in units
                ]
            ),
            vt.cap,
        ),
        "vt_additions": np.array(
            [filer_total(u, "tax_exempt_interest_income") for u in units]
        ),
    }
    for variable, expected in reference.items():
        in_state = is_nd if variable.startswith("nd_") else is_vt
        np.testing.assert_allclose(
            results[variable][:n][in_state],
            expected[in_state],
            atol=TOLERANCE,
            err_msg=variable,
        )
    np.testing.assert_allclose(
        results["us_govt_interest"][:n],
        [filer_total(u, "us_govt_interest_person") for u in units],
        atol=TOLERANCE,
    )


# A simulation's cost is mostly fixed, so each example is a batch of tax
# units and there are few examples.
@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=10, max_size=30))
def test_dependent_capital_income_stays_off_nd_and_vt_returns(units):
    check(units)


def test_reported_examples():
    """The two households that showed the leak (TY2025): in North Dakota a
    head with $50,000 of wages and $1,000 of qualified dividends, and in
    Vermont a head with $150,000 of wages and a $10,000 long-term gain, each
    with a dependent child who has dividends or a Vermont-eligible gain."""
    zero = {name: 0.0 for name in CAPITAL_INPUTS}
    nd = {
        "state": "ND",
        "filers": [
            {
                "age": 40,
                "employment_income": 50_000.0,
                **zero,
                "qualified_dividend_income": 1_000.0,
            }
        ],
        "dependents": [{"age": 10, **zero, "qualified_dividend_income": 5_000.0}],
    }
    vt = {
        "state": "VT",
        "filers": [
            {
                "age": 40,
                "employment_income": 150_000.0,
                **zero,
                "long_term_capital_gains": 10_000.0,
            }
        ],
        "dependents": [
            {
                "age": 10,
                **zero,
                "long_term_capital_gains": 100_000.0,
                "long_term_capital_gains_on_assets_eligible_for_vt_exclusion": 100_000.0,
            }
        ],
    }
    check([nd, vt])
    results, _ = calculate([nd, vt])
    assert results["nd_qdiv_subtraction"][0] == 400
    assert results["vt_percentage_capital_gains_exclusion"][1] == 0
    np.testing.assert_allclose(results["vt_income_tax"][1], 6_623.20, atol=TOLERANCE)
