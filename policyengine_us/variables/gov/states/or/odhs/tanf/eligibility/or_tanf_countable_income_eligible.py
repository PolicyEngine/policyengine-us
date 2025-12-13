from policyengine_us.model_api import *


class or_tanf_countable_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF countable income eligible"
    definition_period = MONTH
    reference = (
        "https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=268185",
        "https://oregon.public.law/rules/oar_461-155-0030",
    )
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = p.maximum_need_group_size
        size_capped = min_(size, max_size)
        additional_people = max_(size - max_size, 0)

        countable_income = spm_unit("or_tanf_countable_income", period)
        countable_limit = (
            p.income.countable_income_limit.amount[size_capped]
            + additional_people
            * p.income.countable_income_limit.additional_person
        )
        return countable_income < countable_limit
