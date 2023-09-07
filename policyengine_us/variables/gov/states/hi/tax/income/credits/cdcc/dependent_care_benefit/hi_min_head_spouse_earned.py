from policyengine_us.model_api import *


class hi_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse for the CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        eligible = head_or_spouse & (
            person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        qualified_children = tax_unit("count_cdcc_eligible", period)
        income = person("earned_income", period)
        one_child_eligible = max_(
            p.dependent_care_benefits.expense_cap.one_child,
            head_or_spouse * income,
        )
        two_or_more_child_eligible = max_(
            p.dependent_care_benefits.expense_cap.two_or_more_child,
            head_or_spouse * income,
        )
        child_eligible_income = where(
            qualified_children <= 1,
            one_child_eligible,
            two_or_more_child_eligible,
        )
        eligible_income = where(
            eligible,
            child_eligible_income,
            head_or_spouse * income,
        )
        # remove impact of income not belong to head/spouse
        head_spouse_income = where(
            head_or_spouse, eligible_income, max(eligible_income)
        )

        return min(head_spouse_income)
