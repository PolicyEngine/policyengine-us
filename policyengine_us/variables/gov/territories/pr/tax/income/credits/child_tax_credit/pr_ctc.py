from policyengine_us.model_api import *


class pr_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
        reduction = tax_unit("pr_ctc_phase_out", period)
        return max_(0, maximum_amount - reduction)