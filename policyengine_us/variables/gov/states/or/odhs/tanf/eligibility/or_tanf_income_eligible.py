from policyengine_us.model_api import *


class or_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF income eligible"
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-160-0100"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf.income
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, 10)
        additional_people = max_(size - 10, 0)

        countable_income = spm_unit("or_tanf_countable_income", period)
        countable_limit_base = p.countable_income_limit.amount[size_capped]
        countable_limit_additional = (
            additional_people * p.countable_income_limit.additional_person
        )
        countable_limit = countable_limit_base + countable_limit_additional
        passes_countable_test = countable_income < countable_limit

        adjusted_income = spm_unit("or_tanf_adjusted_income", period)
        adjusted_limit_base = p.adjusted_income_limit.amount[size_capped]
        adjusted_limit_additional = (
            additional_people * p.adjusted_income_limit.additional_person
        )
        adjusted_limit = adjusted_limit_base + adjusted_limit_additional
        passes_adjusted_test = adjusted_income < adjusted_limit

        return passes_countable_test & passes_adjusted_test
