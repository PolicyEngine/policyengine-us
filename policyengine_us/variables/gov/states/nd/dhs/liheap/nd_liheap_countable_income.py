from policyengine_us.model_api import *


class nd_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Dakota LIHEAP countable income"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_05_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_15.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10_50.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        # Annual inputs approximate the application-month annualization rules.
        # Include nonqualified members' income and deductions, with TANF once.
        income = add(
            spm_unit,
            period,
            [
                "nd_liheap_countable_earned_income",
                "nd_liheap_countable_unearned_income",
                "tanf",
            ],
        )
        person = spm_unit.members
        premiums = person("health_insurance_premiums", period)
        # A positive reported aggregate takes precedence over its components.
        # Otherwise use both nonnegative reported components; do not impute
        # Medicare premiums from the calculated premium variable.
        reported_premiums = where(
            premiums > 0,
            premiums,
            max_(
                person("health_insurance_premiums_without_medicare_part_b", period),
                0,
            )
            + max_(person("medicare_part_b_premiums_reported", period), 0),
        )
        deductions = spm_unit.sum(
            max_(reported_premiums, 0)
            + max_(person("pre_tax_health_insurance_premiums", period), 0)
        ) + add(
            spm_unit,
            period,
            [
                "other_medical_expenses",
                "child_support_expense",
                "alimony_expense",
                "childcare_expenses",
            ],
        )
        # Medical payment plans, legal support obligations and care purpose are
        # not separately observed. Garnishments, payee fees, and qualifying
        # away-from-home expenses lack inputs; no deductions are imputed.
        return max_(income - deductions, 0)
