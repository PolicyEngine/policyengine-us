from policyengine_us.model_api import *


class de_claims_refundable_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Delaware refundable earned income tax credit"
    unit = USD
    documentation = "Whether tax unit selects the refundable or non-refundable earned income tax credit."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        de_tax_liability_if_refundable_eitc = tax_unit(
            "de_tax_liability_if_refundable_eitc", period
        )
        de_tax_liability_if_non_refundable_eitc = tax_unit(
            "de_tax_liability_if_non_refundable_eitc", period
        )
        return (
            de_tax_liability_if_refundable_eitc
            < de_tax_liability_if_non_refundable_eitc
        )
        