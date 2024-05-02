from policyengine_us.model_api import *


class va_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia non-refundable EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # Either claims refundable or non-refundable, but not both.
        claims = ~tax_unit("va_claims_refundable_eitc", period)
        amount_if_claimed = tax_unit(
            "va_non_refundable_eitc_if_claimed", period
        )
        return claims * amount_if_claimed
