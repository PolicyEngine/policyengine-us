from policyengine_us.model_api import *


class ar_tea_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas TEA maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 6.1.1
        p = parameters(period).gov.states.ar.dhs.tea.payment_standard
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_unit_size)
        return p.amount[capped_size]
