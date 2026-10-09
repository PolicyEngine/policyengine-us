"""Fast IRA formula checks that do not import the complete US model.

Execute the actual formula AST with NumPy arithmetic and small entity proxies.
The Decimal oracle uses Publication 590-A's remaining-allowance worksheet and
the separate deductible/designated-contribution categories in IRC 219(c) and
408(o), rather than reproducing the model's reduction or aggregate formulas.

Authorities: https://www.law.cornell.edu/uscode/text/26/219,
https://www.law.cornell.edu/uscode/text/26/408#o_2,
https://www.irs.gov/publications/p590a,
https://www.irs.gov/pub/irs-drop/n-25-67.pdf.

These tests supplement Simulation tests: they do not validate input conversion,
entity construction, parameter loading, dependency cycles, MAGI, or aggregation.
"""

import ast
from decimal import Decimal, ROUND_CEILING
from itertools import product
from pathlib import Path
from types import SimpleNamespace

import numpy as np


VARIABLES = Path(__file__).resolve().parents[1] / "variables"
RETIREMENT = VARIABLES / "household/expense/retirement"
IRA = (
    VARIABLES
    / "gov/irs/income/taxable_income/adjusted_gross_income/above_the_line_deductions/ira"
)
STATUSES = SimpleNamespace(
    SINGLE="SINGLE",
    JOINT="JOINT",
    SEPARATE="SEPARATE",
    HEAD_OF_HOUSEHOLD="HEAD_OF_HOUSEHOLD",
    SURVIVING_SPOUSE="SURVIVING_SPOUSE",
)


class StatusArray(np.ndarray):
    possible_values = STATUSES


class StatusParameter(SimpleNamespace):
    def __getitem__(self, statuses):
        return np.asarray([getattr(self, str(status)) for status in statuses])


class Group:
    def __init__(self, groups, values=None):
        self.groups = np.asarray(groups, dtype=int)
        self.values = values or {}

    def __call__(self, name, period):
        value = self.values[name]
        if name == "filing_status":
            return np.asarray(value).view(StatusArray)
        return np.asarray(value)

    def sum(self, values):
        return np.bincount(self.groups, weights=values)[self.groups]


class People:
    def __init__(self, values, tax_groups=None, tax_values=None, marital_groups=None):
        self.values = {key: np.asarray(value) for key, value in values.items()}
        self.count = len(next(iter(self.values.values())))
        groups = np.arange(self.count) if tax_groups is None else tax_groups
        self.tax_unit = Group(groups, tax_values)
        self.marital_unit = Group(
            np.arange(self.count) if marital_groups is None else marital_groups
        )

    def __call__(self, name, period):
        return self.values.get(name, np.zeros(self.count))


def formula(path, variable):
    """Compile only the repository's formula, excluding model imports/metadata."""
    tree = ast.parse(path.read_text(), filename=str(path))
    variable_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == variable
    )
    function = next(
        node
        for node in variable_class.body
        if isinstance(node, ast.FunctionDef) and node.name == "formula"
    )
    namespace = {
        "np": np,
        "max_": np.maximum,
        "min_": np.minimum,
        "where": np.where,
        "clip": np.clip,
        "add": lambda person, period, names: sum(
            person(name, period) for name in names
        ),
    }
    exec(
        compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"),
        namespace,
    )
    return namespace["formula"]


def parameters():
    starts = StatusParameter(
        SINGLE=81_000,
        JOINT=129_000,
        SEPARATE=0,
        HEAD_OF_HOUSEHOLD=81_000,
        SURVIVING_SPOUSE=129_000,
    )
    widths = StatusParameter(
        SINGLE=10_000,
        JOINT=20_000,
        SEPARATE=10_000,
        HEAD_OF_HOUSEHOLD=10_000,
        SURVIVING_SPOUSE=20_000,
    )
    retirement = SimpleNamespace(
        limit=SimpleNamespace(ira=7_500),
        catch_up=SimpleNamespace(age_threshold=50, limit=SimpleNamespace(ira=1_100)),
    )
    phase_out = SimpleNamespace(
        start=starts,
        width=widths,
        spouse_start=242_000,
        spouse_width=10_000,
        minimum=200,
        rounding_interval=10,
    )
    root = SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                gross_income=SimpleNamespace(retirement_contributions=retirement),
                ald=SimpleNamespace(ira=SimpleNamespace(phase_out=phase_out)),
            )
        )
    )
    return lambda period: root


def decimal(value):
    return Decimal(str(value))


def worksheet_allowance(age, status, active, spouse_active, lived_together, income):
    """Pub. 590-A Worksheet 1-2: round the remaining allowance upwards."""
    annual_allowance = Decimal(8_600 if age >= 50 else 7_500)
    if status == "SEPARATE" and lived_together:
        covered = active or spouse_active
        lower, upper = 0, 10_000
    elif active:
        covered = True
        lower, upper = (
            (129_000, 149_000)
            if status in ("JOINT", "SURVIVING_SPOUSE")
            else (81_000, 91_000)
        )
    elif status == "JOINT" and spouse_active:
        covered = True
        lower, upper = 242_000, 252_000
    else:
        covered = False
        lower, upper = 0, 1
    if not covered or decimal(income) <= lower:
        return annual_allowance
    if decimal(income) >= upper:
        return Decimal(0)
    remaining_fraction = (Decimal(upper) - decimal(income)) / Decimal(upper - lower)
    remaining = annual_allowance * remaining_fraction
    rounded = (remaining / Decimal(10)).to_integral_value(rounding=ROUND_CEILING) * 10
    return max(Decimal(200), rounded)


def test_phaseout_matches_decimal_irs_worksheet_across_coverage_and_boundaries():
    rows = []
    expected = []
    tax_groups = []
    incomes = [
        0,
        0.01,
        9_999.99,
        10_000,
        80_999.99,
        81_000,
        81_013.33,
        81_013.34,
        90_800,
        90_999.99,
        91_000,
        128_999.99,
        129_000,
        129_026.66,
        129_026.67,
        139_000,
        148_999.99,
        149_000,
        241_999.99,
        242_000,
        242_013.33,
        242_013.34,
        247_000,
        251_999.99,
        252_000,
        300_000,
    ]
    for age, status, active, spouse_active, together in product(
        [40, 50], vars(STATUSES), [False, True], [False, True], [False, True]
    ):
        for income in incomes:
            index = len(rows)
            rows.extend(
                [
                    (age, status, active, together, income),
                    (age, status, spouse_active, together, income),
                ]
            )
            tax_groups.extend([index, index if status == "JOINT" else index + 1])
            expected.append(
                float(
                    worksheet_allowance(
                        age, status, active, spouse_active, together, income
                    )
                )
            )
    people = People(
        {
            "age": [row[0] for row in rows],
            "ira_active_participant": [row[2] for row in rows],
            "is_tax_unit_head_or_spouse": np.ones(len(rows), dtype=bool),
        },
        tax_groups,
        {
            "filing_status": [row[1] for row in rows],
            "cohabitating_spouses": [row[3] for row in rows],
            "ira_219g_magi": [row[4] for row in rows],
        },
        np.arange(len(rows)) // 2,
    )
    actual = formula(IRA / "ira_219g_deductible_limit.py", "ira_219g_deductible_limit")(
        people, None, parameters()
    )
    np.testing.assert_array_equal(actual[::2], expected)
    assert np.all(np.isfinite(actual))
    assert np.all((actual == 0) | (actual >= 200))
    assert np.all(actual % 10 == 0)
    assert np.all(np.diff(actual[::2].reshape(-1, len(incomes)), axis=1) <= 0)


def legal_spouse_consumption(age, compensation, traditional, roth, phaseout):
    """Account separately for deductible, designated, and Roth contributions."""
    dollar = Decimal(8_600 if age >= 50 else 7_500)
    compensation, traditional, roth, phaseout = map(
        decimal, [compensation, traditional, roth, phaseout]
    )
    deductible = max(Decimal(0), min(traditional, compensation, dollar, phaseout))
    designated = max(
        Decimal(0),
        min(traditional - deductible, compensation - deductible, dollar - deductible),
    )
    return deductible + designated + max(Decimal(0), roth)


def reference_joint_deductions(ages, compensation, traditional, roth, phaseout):
    result = []
    for index in range(2):
        other = 1 - index
        available = decimal(compensation[index])
        if compensation[index] < compensation[other]:
            other_consumed = legal_spouse_consumption(
                ages[other],
                compensation[other],
                traditional[other],
                roth[other],
                phaseout[other],
            )
            available += max(Decimal(0), decimal(compensation[other]) - other_consumed)
        result.append(
            float(
                max(
                    Decimal(0),
                    min(
                        decimal(traditional[index]), available, decimal(phaseout[index])
                    ),
                )
            )
        )
    return result


def test_actual_excess_contributions_match_statutory_spousal_categories():
    rows = []
    expected = []
    for (
        higher,
        lower,
        traditional,
        roth,
        lower_request,
        higher_phaseout,
        age,
    ) in product(
        [6_000, 10_000, 15_000],
        [0, 500, 6_000],
        [0, 6_000, 12_000],
        [0, 5_000, 12_000],
        [0, 7_500, 12_000],
        [0, 200, 7_500],
        [40, 50],
    ):
        # Include role swaps: the taxpayer with more compensation need not be head.
        for reverse in [False, True]:
            ages = [age, 40]
            compensation = [higher, lower]
            traditionals = [traditional, lower_request]
            roths = [roth, 0]
            limits = [higher_phaseout, 7_500]
            if reverse:
                ages, compensation, traditionals, roths, limits = (
                    values[::-1]
                    for values in [ages, compensation, traditionals, roths, limits]
                )
            rows.extend(zip(ages, compensation, traditionals, roths, limits))
            expected.extend(
                reference_joint_deductions(
                    ages, compensation, traditionals, roths, limits
                )
            )
    count = len(rows)
    people = People(
        {
            "age": [row[0] for row in rows],
            "ira_compensation": [row[1] for row in rows],
            "traditional_ira_contributions": [row[2] for row in rows],
            "roth_ira_contributions": [row[3] for row in rows],
            "ira_219g_deductible_limit": [row[4] for row in rows],
            "is_tax_unit_head_or_spouse": np.ones(count, dtype=bool),
            "is_tax_unit_head": np.arange(count) % 2 == 0,
            "is_tax_unit_spouse": np.arange(count) % 2 == 1,
        },
        np.arange(count) // 2,
        {"tax_unit_is_joint": np.ones(count, dtype=bool)},
    )
    actual = formula(IRA / "traditional_ira_deduction.py", "traditional_ira_deduction")(
        people, None, parameters()
    )
    np.testing.assert_array_equal(actual, expected)
    assert np.all(actual >= 0)
    assert np.all(actual <= people("traditional_ira_contributions", None))
    assert np.all(actual <= people("ira_219g_deductible_limit", None))
    assert np.all(
        actual.reshape(-1, 2).sum(axis=1)
        <= people("ira_compensation", None).reshape(-1, 2).sum(axis=1)
    )


def test_compensation_excludes_losses_and_passive_income():
    examples = [
        ({"irs_employment_income": 1_000, "self_employment_income": -500}, 1_000),
        ({"taxable_alimony_income": 2_500}, 2_500),
        ({"self_employment_income": 300, "self_employment_tax_ald_person": 500}, 0),
        (
            {
                "farm_operations_income": 7_500,
                "self_employment_tax_ald_person": 530,
                "self_employed_pension_contribution_ald_person": 1_000,
            },
            5_970,
        ),
        (
            {
                "partnership_self_employment_net_earnings": 8_500,
                "self_employment_tax_ald_person": 600,
            },
            7_900,
        ),
        (
            {
                "sstb_self_employment_income": 9_000,
                "self_employment_tax_ald_person": 636,
                "self_employed_pension_contribution_ald_person": 1_000,
            },
            7_364,
        ),
        (
            {
                "irs_employment_income": 1_000,
                "taxable_alimony_income": 500,
                "self_employment_income": 3_000,
                "sstb_self_employment_income": -1_000,
                "farm_operations_income": 2_000,
                "partnership_self_employment_net_earnings": 5_000,
                "self_employment_tax_ald_person": 300,
                "self_employed_pension_contribution_ald_person": 1_000,
            },
            9_200,
        ),
        (
            {
                "pension_income": 50_000,
                "rental_income": 10_000,
                "dividend_income": 10_000,
            },
            0,
        ),
    ]
    names = set().union(*(values for values, _ in examples))
    people = People(
        {name: [values.get(name, 0) for values, _ in examples] for name in names}
    )
    actual = formula(RETIREMENT / "ira_compensation.py", "ira_compensation")(
        people, None, parameters()
    )
    np.testing.assert_array_equal(actual, [expected for _, expected in examples])


def test_dependents_neither_claim_deduction_nor_supply_spousal_compensation():
    calculate = formula(
        IRA / "traditional_ira_deduction.py", "traditional_ira_deduction"
    )
    for joint, expected in [(True, [5_000, 1_000, 0]), (False, [5_000, 0, 0])]:
        people = People(
            {
                "age": [40, 40, 17],
                "ira_compensation": [6_000, 0, 20_000],
                "traditional_ira_contributions": [5_000, 7_500, 1_000],
                "roth_ira_contributions": [0, 0, 0],
                "ira_219g_deductible_limit": [7_500, 7_500, 7_500],
                "is_tax_unit_head_or_spouse": [True, True, False],
                "is_tax_unit_head": [True, False, False],
                "is_tax_unit_spouse": [False, True, False],
            },
            [0, 0, 0],
            {"tax_unit_is_joint": [joint, joint, joint]},
        )
        np.testing.assert_array_equal(calculate(people, None, parameters()), expected)


def test_compensation_has_unit_wage_effect_and_passive_income_irrelevance():
    calculate = formula(RETIREMENT / "ira_compensation.py", "ira_compensation")
    losses = np.arange(-10_000, 1, 100)
    baseline = People(
        {
            "irs_employment_income": np.full(len(losses), 3_000),
            "self_employment_income": losses,
        }
    )
    modified = People(
        {
            **baseline.values,
            "irs_employment_income": np.full(len(losses), 3_123.45),
            "pension_income": np.full(len(losses), 100_000),
        }
    )
    before = calculate(baseline, None, parameters())
    after = calculate(modified, None, parameters())
    np.testing.assert_array_equal(before, np.full(len(losses), 3_000))
    np.testing.assert_allclose(after - before, 123.45, rtol=0, atol=1e-10)


def test_generated_single_contributions_preserve_shares_within_compensation():
    rows = list(
        product(
            [0, 0.25, 0.5, 2_000, 10_000],
            [0, 0.25, 1_000, 8_000],
            [0, 0.25, 1_000, 8_000],
            [40, 50],
        )
    )
    people = People(
        {
            "ira_compensation": [row[0] for row in rows],
            "traditional_ira_contributions_desired": [row[1] for row in rows],
            "roth_ira_contributions_desired": [row[2] for row in rows],
            "age": [row[3] for row in rows],
            "is_tax_unit_head_or_spouse": np.ones(len(rows), dtype=bool),
        },
        tax_values={"tax_unit_is_joint": np.zeros(len(rows), dtype=bool)},
    )
    limit = formula(RETIREMENT / "ira_contribution_limit.py", "ira_contribution_limit")(
        people, None, parameters()
    )
    people.values["ira_contribution_limit"] = limit
    scale = formula(RETIREMENT / "ira_contribution_scale.py", "ira_contribution_scale")(
        people, None, parameters()
    )
    traditional = people("traditional_ira_contributions_desired", None) * scale
    roth = people("roth_ira_contributions_desired", None) * scale
    assert np.all(np.isfinite(scale))
    assert np.all((scale >= 0) & (scale <= 1))
    assert np.all(traditional + roth <= people("ira_compensation", None) + 1e-8)
    assert np.all(
        traditional + roth <= np.where(people("age", None) >= 50, 8_600, 7_500) + 1e-8
    )
    np.testing.assert_allclose(
        traditional * people("roth_ira_contributions_desired", None),
        roth * people("traditional_ira_contributions_desired", None),
        rtol=1e-12,
        atol=1e-8,
    )
    assert np.all(
        scale[
            (people("ira_compensation", None) == 0.5)
            & (people("traditional_ira_contributions_desired", None) == 0.25)
            & (people("roth_ira_contributions_desired", None) == 0.25)
        ]
        == 1
    )
