from openfisca_us.model_api import *


class ctc_value_received(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child Tax Credit value received"
    unit = USD
    documentation = "Child Tax Credit value received, between the refundable element and the non-refundable element capped at limiting tax liability."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#a"
    # This variable is not used for CTC computation.
    # It is only for debugging and contributed variables.

    def formula(tax_unit, period, parameters):
        ctc_limiting_tax_liability = tax_unit(
            "ctc_limiting_tax_liability", period
        )
        refundable_ctc = tax_unit("refundable_ctc", period)
        non_refundable_ctc = tax_unit("non_refundable_ctc", period)
        non_refundable_ctc_value = min_(
            non_refundable_ctc, ctc_limiting_tax_liability
        )
        return refundable_ctc + non_refundable_ctc_value
