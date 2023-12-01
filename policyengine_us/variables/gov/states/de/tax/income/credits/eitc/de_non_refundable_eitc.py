from policyengine_us.model_api import *


class de_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware non-refundable EITC"
    unit = USD
    documentation = "Non-refundable EITC credit reducing DE State income tax."
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # Either claims refundable or non-refundable, but not both.
        claims = ~tax_unit("de_claims_refundable_eitc", period)
        amount_if_claimed = tax_unit(
            "de_non_refundable_eitc_if_claimed", period
        )
        return claims * amount_if_claimed
