from policyengine_us.model_api import *


class pr_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf#page=1"

    # This provision is part of the federal CTC legal code
    # will will merge the logic with the federal CTC once the puerto income tax structure is completed
    def formula(tax_unit, period, parameters):
        maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
        reduction = tax_unit("pr_ctc_phase_out", period)
        return max_(0, maximum_amount - reduction)
