from policyengine_us.model_api import *


class dc_tanf_maximum_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF maximum income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.dc.dhs.tanf.eligibility.maximum_income
        base = p.main[unit_size]
        # TODO: Add childcare addition.
        return base * MONTHS_IN_YEAR
