from policyengine_us.model_api import *


class il_tanf_payment_level_for_initial_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) payment level for initial eligibility"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.payment_level
        fpg = spm_unit("spm_unit_fpg", period)

        return p.rate * fpg
