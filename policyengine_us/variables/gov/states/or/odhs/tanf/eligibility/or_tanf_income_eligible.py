from policyengine_us.model_api import *


class or_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF income eligible"
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-160-0100"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = p.maximum_need_group_size
        size_capped = min_(size, max_size)
        additional_people = max_(size - max_size, 0)

        countable_income = spm_unit("or_tanf_countable_income", period)

        # Standard test: countable < limit AND adjusted < limit
        countable_limit = (
            p.income.countable_income_limit.amount[size_capped]
            + additional_people
            * p.income.countable_income_limit.additional_person
        )
        passes_countable_test = countable_income < countable_limit

        adjusted_income = spm_unit("or_tanf_adjusted_income", period)
        adjusted_limit = (
            p.income.adjusted_income_limit.amount[size_capped]
            + additional_people
            * p.income.adjusted_income_limit.additional_person
        )
        passes_adjusted_test = adjusted_income < adjusted_limit

        passes_standard_test = passes_countable_test & passes_adjusted_test

        # ELI test: countable < (payment_standard * multiplier)
        payment_standard = spm_unit("or_tanf_payment_standard", period)
        eli_limit = payment_standard * p.income.eli_multiplier
        passes_eli_test = countable_income < eli_limit

        eli_eligible = spm_unit("or_tanf_eli_eligible", period)
        return where(eli_eligible, passes_eli_test, passes_standard_test)
