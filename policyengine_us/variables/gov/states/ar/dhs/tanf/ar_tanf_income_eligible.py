from policyengine_us.model_api import *


class ar_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TANF income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.3
        # Income eligibility standard is $223/month for ALL family sizes
        p = parameters(
            period
        ).gov.states.ar.dhs.tanf.income.eligibility_standard
        countable_income = spm_unit("ar_tanf_countable_income", period)
        return countable_income <= p.amount
