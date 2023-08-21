from policyengine_us.model_api import *


class va_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Earned Income Tax Credit"
    unit = USD
    documentation = "Refundable or non-refundable Virginia EITC"
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=26"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        refundable_eitc = tax_unit("va_refundable_eitc", period)
        non_refundable_eitc = tax_unit("va_non_refundable_eitc", period)
        claims_refundable = tax_unit("va_claims_refundable_eitc", period)
        return where(claims_refundable, refundable_eitc, non_refundable_eitc)
