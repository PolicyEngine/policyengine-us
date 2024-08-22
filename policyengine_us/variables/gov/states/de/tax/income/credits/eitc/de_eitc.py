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
        claims_refundable = tax_unit("de_claims_refundable_eitc", period)
        return where(claims_refundable, refundable_eitc, non_refundable_eitc)
