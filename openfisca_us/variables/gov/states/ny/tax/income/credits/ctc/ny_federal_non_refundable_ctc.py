from openfisca_us.model_api import *


class ny_federal_non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY federal non-refundable CTC"
    unit = USD
    documentation = "The version of the federal non-refundable CTC used to determine the NY Empire State Child Credit."
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        max_amount = tax_unit("ny_federal_ctc_max", period)
        limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
        return min_(max_amount, limiting_tax)
