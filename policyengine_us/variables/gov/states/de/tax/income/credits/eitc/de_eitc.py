from policyengine_us.model_api import *


class de_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware EITC"
    unit = USD
    documentation = "Refundable or non-refundable Delaware EITC"
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        refundable_eitc = tax_unit("de_refundable_eitc", period)
        non_refundable_eitc = tax_unit("de_non_refundable_eitc", period)
        claims_refundable_based_on_tax_liability = tax_unit(
            "de_claims_refundable_eitc", period
        )
        claims_refundable_by_default = tax_unit(
            "de_eitc_non_default_refundability", period
        )
        claims_refundable = where(
            claims_refundable_by_default,
            claims_refundable_based_on_tax_liability,
            True,
        )
        return where(claims_refundable, refundable_eitc, non_refundable_eitc)
