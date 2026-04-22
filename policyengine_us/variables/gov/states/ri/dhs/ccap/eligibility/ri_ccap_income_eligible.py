from policyengine_us.model_api import *


class ri_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Rhode Island CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.6.1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.income.fpl_rate
        countable_income = spm_unit("ri_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        enrolled = spm_unit("ri_ccap_enrolled", period)
        initial_limit = fpg * p.initial_eligibility
        transitional_limit = fpg * p.transitional
        income_limit = where(
            enrolled,
            transitional_limit,
            initial_limit,
        )
        return countable_income <= income_limit
