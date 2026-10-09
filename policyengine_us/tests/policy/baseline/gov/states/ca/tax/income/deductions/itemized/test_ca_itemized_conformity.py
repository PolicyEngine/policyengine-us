"""California itemized deductions must remain independent of federal reforms.

Use leaf expense facts in vectorized household situations. Paired California
and New York households also guard against changes leaking into federal
charitable or miscellaneous deductions.
"""

from random import Random

import numpy as np
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation


YEARS = (2025, 2026, 2027)
CA_VARIABLES = (
    "ca_itemized_deductions_pre_limitation",
    "ca_itemized_deductions",
    "ca_deductions",
    "ca_amti_adjustments",
    "ca_pre_exemption_amti",
    "ca_amti",
    "ca_charitable_deduction",
    "ca_misc_deduction",
)
FEDERAL_VARIABLES = (
    "charitable_deduction",
    "misc_deduction",
    "itemized_deductions_less_salt",
)


class ChangeFederalItemizedRules(Reform):
    """Make federal rules conspicuously different throughout the test years."""

    def apply(self):
        def modify(parameters):
            itemized = parameters.gov.irs.deductions.itemized
            updates = (
                (itemized.charity.floor.applies, True),
                (itemized.charity.floor.amount, 0.25),
                (itemized.charity.ceiling.all, 0.10),
                (itemized.charity.ceiling.non_cash, 0.10),
                (itemized.charity.ceiling.non_cash_to_non_50_pct_org, 0.10),
                (itemized.misc.applies, True),
                (itemized.misc.floor, 0),
            )
            for parameter, value in updates:
                parameter.update(
                    start=instant("2025-01-01"),
                    stop=instant("2027-12-31"),
                    value=value,
                )
            return parameters

        self.modify_parameters(modify)


def _generated_facts():
    """Seeded bounded facts preserve the subset relationship of noncash gifts."""
    random = Random(17076)
    facts = []
    for _ in range(24):
        income = random.randint(-20_000, 250_000)
        cash = random.randint(0, 160_000)
        noncash = random.randint(0, 160_000)
        noncash_non50 = random.randint(0, noncash)
        employee_expenses = random.randint(0, 300_000)
        preparation_fees = random.randint(0, 6_000)
        facts.append(
            (
                income,
                cash,
                noncash,
                noncash_non50,
                employee_expenses,
                preparation_fees,
            )
        )
    return facts


def _all_years(value):
    return {str(year): value for year in YEARS}


def _situation(facts):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for case_index, fact in enumerate(facts):
        income, cash, noncash, noncash_non50, employee, preparation = fact
        # Third row raises two independent leaf expenses at unchanged income.
        for variant, state in enumerate(("CA", "NY", "CA")):
            identifier = f"case_{case_index}_{variant}"
            increase = 1_000 if variant == 2 else 0
            situation["people"][identifier] = {
                "age": _all_years(40),
                "employment_income": _all_years(income),
                "charitable_cash_donations": _all_years(cash + increase),
                "charitable_non_cash_donations": _all_years(noncash),
                "charitable_non_cash_donations_non_50_pct_orgs": _all_years(
                    noncash_non50
                ),
                "unreimbursed_business_employee_expenses": _all_years(employee),
                "tax_preparation_fees": _all_years(preparation + increase),
            }
            for entity in (
                "tax_units",
                "spm_units",
                "families",
                "marital_units",
                "households",
            ):
                situation[entity][identifier] = {"members": [identifier]}
            situation["tax_units"][identifier]["filing_status"] = _all_years("SINGLE")
            situation["households"][identifier]["state_code"] = _all_years(state)
    return situation


def test_ca_itemized_rules_are_independent_vectorized_and_monotone():
    # Anchors force both state deduction choices and a substantive federal
    # reform effect, rather than letting a run of zero gifts pass vacuously.
    facts = [
        (50_000, 0, 0, 0, 0, 0),
        (100_000, 30_000, 0, 0, 10_000, 0),
        (200_000, 0, 0, 0, 100_000, 0),
        (200_000, 0, 0, 0, 300_000, 0),
        (50_000, 0, 0, 0, 150_000, 0),
        (20_000, 0, 0, 0, 100_000, 0),
        (50_000, 0, 0, 0, 51_000, 0),
        (50_000, 0, 0, 0, 50_999, 0),
        (-10_000, 1_000, 1_000, 500, 1_000, 100),
        (0, 1_000, 1_000, 500, 1_000, 100),
        (100_000, 100, 0, 0, 1_999, 0),
        (100_000, 100, 0, 0, 2_000, 0),
        (100_000, 100, 0, 0, 2_001, 0),
        (100_000, 49_999, 0, 0, 0, 0),
        (100_000, 50_000, 0, 0, 0, 0),
        (100_000, 50_001, 0, 0, 0, 0),
        (100_000, 0, 30_000, 30_000, 0, 0),
        (100_000, 0, 30_001, 30_001, 0, 0),
        *_generated_facts(),
    ]
    situation = _situation(facts)
    baseline = Simulation(situation=situation, start_instant="2025-01-01")
    reformed = Simulation(
        situation=situation,
        tax_benefit_system=baseline.tax_benefit_system,
        reform=ChangeFederalItemizedRules,
        start_instant="2025-01-01",
    )
    ca = np.arange(0, len(facts) * 3, 3)
    ny = ca + 1
    increased = ca + 2

    for year in YEARS:
        for variable in CA_VARIABLES:
            original = baseline.calculate(variable, year)
            changed = reformed.calculate(variable, year)
            np.testing.assert_allclose(original, changed, atol=0.02, rtol=0)
            np.testing.assert_array_equal(original[ny], 0)

        # Changing the state never changes these federal deduction rules.
        for variable in FEDERAL_VARIABLES:
            result = baseline.calculate(variable, year)
            np.testing.assert_allclose(result[ca], result[ny], atol=0.02, rtol=0)

        assert not np.array_equal(
            baseline.calculate("charitable_deduction", year),
            reformed.calculate("charitable_deduction", year),
        )
        assert not np.array_equal(
            baseline.calculate("misc_deduction", year),
            reformed.calculate("misc_deduction", year),
        )

        positive_agi = baseline.calculate("positive_agi", year)
        charity = baseline.calculate("ca_charitable_deduction", year)
        misc = baseline.calculate("ca_misc_deduction", year)
        total_misc = baseline.calculate("total_misc_deductions", year)
        total_gifts = np.array([fact[1] + fact[2] for fact in facts])
        assert np.all(charity[ca] >= 0)
        assert np.all(charity[ca] <= total_gifts + 0.02)
        assert np.all(charity[ca] <= positive_agi[ca] * 0.5 + 0.02)
        assert np.all(misc[ca] >= 0)
        assert np.all(misc[ca] <= total_misc[ca] + 0.02)

        # An extra dollar of cash gifts or misc expenses cannot reduce its
        # deduction, or increase that deduction by more than a dollar.
        for result in (charity, misc):
            delta = result[increased] - result[ca]
            assert np.all(delta >= -0.02)
            assert np.all(delta <= 1_000.02)
        above_misc_floor = total_misc[ca] >= positive_agi[ca] * 0.02
        np.testing.assert_allclose(
            (misc[increased] - misc[ca])[above_misc_floor],
            1_000,
            atol=0.02,
            rtol=0,
        )

        itemized = baseline.calculate("ca_itemized_deductions", year)
        standard = baseline.calculate("ca_standard_deduction", year)
        chosen = baseline.calculate("ca_deductions", year)
        np.testing.assert_array_equal(
            chosen[ca], np.maximum(itemized[ca], standard[ca])
        )
        assert itemized[ca[0]] < standard[ca[0]]
        assert itemized[ca[1]] > standard[ca[1]]

        # Schedule P line 15 retains the signed AGI less deductions before
        # adding back AMT-disallowed deductions. These wage, gift, and misc
        # facts have no AMT preferences that could raise AMTI above AGI.
        agi = baseline.calculate("ca_agi", year)
        adjustments = baseline.calculate("ca_amti_adjustments", year)
        limitation = baseline.calculate("ca_itemized_deductions_limitation", year)
        pre_exemption_amti = baseline.calculate("ca_pre_exemption_amti", year)
        amti = baseline.calculate("ca_amti", year)
        form_amti = agi - chosen + adjustments - limitation
        np.testing.assert_allclose(
            pre_exemption_amti[ca], form_amti[ca], atol=0.02, rtol=0
        )
        # Every generated tax unit is single, so the separate-filer AMTI
        # adjustment does not apply.
        np.testing.assert_allclose(amti[ca], form_amti[ca], atol=0.02, rtol=0)
        assert np.all(pre_exemption_amti[ca] <= agi[ca] + 0.02)

        excess_deductions = chosen[ca] > agi[ca]
        assert np.any(excess_deductions)
        assert np.any(chosen[ca] == agi[ca])
        assert np.any(np.isclose(agi[ca] - chosen[ca], 1, atol=0.02, rtol=0))
        assert chosen[ca[2]] < agi[ca[2]]
        assert pre_exemption_amti[ca[2]] > 0

        exemption = baseline.tax_benefit_system.parameters(
            f"{year}-01-01"
        ).gov.states.ca.tax.income.amt.exemption.amount.SINGLE
        below_exemption_excess = excess_deductions & (agi[ca] < exemption)
        assert np.any(below_exemption_excess)
        amt = baseline.calculate("ca_amt", year)
        np.testing.assert_array_equal(amt[ca[below_exemption_excess]], 0)
        # High-income filers can owe AMT when disallowed deductions exceed
        # income; the zero-AMT invariant requires income below the exemption.
        assert excess_deductions[3]
        assert amt[ca[3]] > 0
