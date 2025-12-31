from policyengine_us.model_api import *


class de_tanf_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF standard of need"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/dss/tanf/",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.tanf
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.payment_standard.max_unit_size)
        return p.income.standard_of_need.amount[capped_unit_size]
