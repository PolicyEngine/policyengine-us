from policyengine_us.model_api import *


class va_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Earned Income Tax Credit"
    unit = USD
    documentation = "Refundable or non-refundable Virginia EITC"
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        refundable_eitc = tax_unit("va_refundable_eitc", period)
        non_refundable_eitc = tax_unit("va_non_refundable_eitc", period)
        claims_refundable = tax_unit("va_claims_refundable_eitc", period)
        amount = where(claims_refundable, refundable_eitc, non_refundable_eitc)
        filing_status = tax_unit("filing_status", period)
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        person = tax_unit.members
        va_eitc_person = person("va_eitc_person", period)
        return where(is_separate, va_eitc_person, amount)
