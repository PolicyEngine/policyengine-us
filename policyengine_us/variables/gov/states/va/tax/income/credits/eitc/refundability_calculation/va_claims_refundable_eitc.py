from policyengine_us.model_api import *


class va_claims_refundable_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer claims refundable Virginia EITC"
    documentation = "Whether the filer claims the refundable over the non-refundable Virginia Earned Income Tax Credit."
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        va_income_tax_if_claiming_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_refundable_eitc", period
        )
        va_income_tax_if_claiming_non_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_non_refundable_eitc", period
        )
        return (
            va_income_tax_if_claiming_refundable_eitc
            < va_income_tax_if_claiming_non_refundable_eitc
        )
