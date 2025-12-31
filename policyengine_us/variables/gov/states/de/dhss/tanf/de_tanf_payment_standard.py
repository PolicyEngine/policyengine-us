from policyengine_us.model_api import *


class de_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/dss/tanf/",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.tanf.payment_standard
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        return p.amount[capped_unit_size]
