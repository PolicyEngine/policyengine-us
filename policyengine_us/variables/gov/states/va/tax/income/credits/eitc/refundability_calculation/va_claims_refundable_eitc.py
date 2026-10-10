from policyengine_us.model_api import *


class va_claims_refundable_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer claims refundable Virginia EITC"
    documentation = "Whether the filer claims the refundable over the non-refundable Virginia Earned Income Tax Credit."
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # A filer who claims the benefits that bar the credits (Va. Code
        # 58.1-339.8(D)) claims neither form of the EITC.
        claims_benefits = tax_unit("va_claims_eitc_disqualifying_benefits", period)
        va_income_tax_if_claiming_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_refundable_eitc", period
        )
        va_income_tax_if_claiming_non_refundable_eitc = tax_unit(
            "va_income_tax_if_claiming_non_refundable_eitc", period
        )
        return ~claims_benefits & (
            va_income_tax_if_claiming_refundable_eitc
            < va_income_tax_if_claiming_non_refundable_eitc
        )
