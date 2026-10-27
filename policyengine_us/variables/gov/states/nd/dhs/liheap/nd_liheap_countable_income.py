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
        "https://liheapch.acf.gov/docs/2026/state-plans/ND_Plan_2026.pdf#page=6",
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
        direct_premiums = person("health_insurance_premiums", period)
        # Manual 415-25-05-05-05 allows "Medicare premiums, deductibles, and
        # co-pays", except "Part A and B Medicare premiums for an individual
        # who is QMB/SLMB, QI-1 or Buy-In eligible". Plan item 1.9 counts
        # Social Security "Excluding MediCare deduction". The Part A and Part B
        # premium variables are each member's out-of-pocket premiums, zero for
        # a member who is not enrolled, whose premium a Medicare Savings
        # Program pays, or (for Part A) who has premium-free Part A; no Part D
        # premium variable exists.
        component_premiums = (
            max_(
                person("health_insurance_premiums_without_medicare_part_b", period),
                0,
            )
            + person("medicare_part_a_premium", period)
            + person("medicare_part_b_premium", period)
        )
        # A positive direct premium input takes precedence over its components.
        premiums = where(direct_premiums > 0, direct_premiums, component_premiums)
        deductions = spm_unit.sum(
            premiums + max_(person("pre_tax_health_insurance_premiums", period), 0)
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
