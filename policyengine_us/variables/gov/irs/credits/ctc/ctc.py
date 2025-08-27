from policyengine_us.model_api import *


class ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child Tax Credit"
    unit = USD
    documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
    definition_period = YEAR
    defined_for = "filer_meets_ctc_identification_requirements"
    reference = "https://www.law.cornell.edu/uscode/text/26/24#a"

    def formula(tax_unit, period, parameters):
        maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
        reduction = tax_unit("ctc_phase_out", period)
        return max_(0, maximum_amount - reduction)
