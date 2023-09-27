from policyengine_us.model_api import *


class de_claims_refundable_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer claims refundable Delaware EITC"
    unit = USD
    documentation = "Whether the filer claims the refundable over the non-refundable Delaware Earned Income Tax Credit."
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        de_income_tax_if_claiming_refundable_eitc = tax_unit(
            "de_income_tax_if_claiming_refundable_eitc", period
        )
        de_income_tax_if_claiming_non_refundable_eitc = tax_unit(
            "de_income_tax_if_claiming_non_refundable_eitc", period
        )
        return (
            de_income_tax_if_claiming_refundable_eitc
            < de_income_tax_if_claiming_non_refundable_eitc
        )
