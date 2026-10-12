from policyengine_us.model_api import *


class sd_cca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Dakota CCA countable income"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=37"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.income
        gross_income = spm_unit("sd_cca_gross_income", period)
        person = spm_unit.members
        # Self-employment income is floored at zero per person (Section 6), so
        # the child exclusion and 4% disregard operate on the same figure that
        # entered gross income.
        person_earned = add(
            person,
            period,
            ["employment_income", "sd_cca_self_employment_income"],
        )
        age = person("age", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # BEES Section 8.3.1 excludes earnings of a child only when the child is
        # not the Primary Applicant or Primary Partner. Tax-unit head/spouse is
        # the available proxy, so a minor applicant parent's earnings count.
        is_excluded_minor = (
            age < p.child_earned_income_exclusion_age
        ) & ~is_head_or_spouse
        excluded_minor_earned_income = spm_unit.sum(is_excluded_minor * person_earned)
        # A 4% standard deduction applies to all remaining earned income,
        # including the earnings of a minor tax-unit head or spouse.
        counted_earned_income = spm_unit.sum(~is_excluded_minor * person_earned)
        earned_disregard = max_(counted_earned_income, 0) * p.earned_income_disregard
        # Court-ordered child support paid out is deducted.
        child_support_expense = add(spm_unit, period, ["child_support_expense"])
        return max_(
            gross_income
            - excluded_minor_earned_income
            - earned_disregard
            - child_support_expense,
            0,
        )
