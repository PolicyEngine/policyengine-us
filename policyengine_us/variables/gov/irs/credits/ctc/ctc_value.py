from policyengine_us.model_api import *


class ctc_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC value"
    unit = USD
    documentation = "Actual value of the Child Tax Credit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return min_(
            tax_unit("ctc", period),
            tax_unit("ctc_phase_in", period),
        )
