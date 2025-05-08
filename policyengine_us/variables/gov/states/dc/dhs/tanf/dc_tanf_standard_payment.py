from policyengine_us.model_api import *


class dc_tanf_standard_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) standard payment"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf.standard_payment
        capped_unit_size = min_(unit_size, p.max_unit_size)
        return p.amount[capped_unit_size]
