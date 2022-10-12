from policyengine_us.model_api import *


class eitc_agi_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum AGI to qualify for EITC"
    documentation = "Used for state-level policies, not EITC computations"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD

    def formula(tax_unit, period, parameters):
        phase_out_start = tax_unit("eitc_phase_out_start", period)
        maximum = tax_unit("eitc_maximum", period)
        phase_out_rate = tax_unit("eitc_phase_out_rate", period)
        agi_beyond_phase_out_start = maximum / phase_out_rate
        return phase_out_start + agi_beyond_phase_out_start
