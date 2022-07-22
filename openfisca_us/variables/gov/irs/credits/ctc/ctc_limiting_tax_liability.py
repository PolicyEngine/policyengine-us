from openfisca_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = "The tax liability used to determine the maximum amount of the non-refundable CTC."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        non_refundable_credits = parameters(
            period
        ).gov.irs.credits.non_refundable
        total_credits = sum(
            [
                tax_unit(credit, period)
                for credit in non_refundable_credits
                if credit != "non_refundable_ctc"
            ]
        )
        return tax_unit("income_tax_before_credits", period) - total_credits
