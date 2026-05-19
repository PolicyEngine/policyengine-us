from policyengine_us.model_api import *


class or_tanf_eli_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF ELI income eligible"
    definition_period = MONTH
    reference = (
        "https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=268185",
        "https://oregon.public.law/rules/oar_461-155-0030",
    )
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        countable_income = spm_unit("or_tanf_countable_income", period)
        payment_standard = spm_unit("or_tanf_payment_standard", period)
        eli_limit = payment_standard * p.income.eli_multiplier
        return countable_income < eli_limit
