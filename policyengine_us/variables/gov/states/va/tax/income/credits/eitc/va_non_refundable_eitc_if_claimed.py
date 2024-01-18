from policyengine_us.model_api import *


class va_non_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia non-refundable EITC if claimed"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.va.tax.income.credits.eitc.match
        # The filer can either claim the non-refundable EITC or the low income credit.
        va_non_refundable_eitc = p.non_refundable * federal_eitc
        low_income_credit = tax_unit("va_low_income_tax_credit", period)
        return max_(va_non_refundable_eitc, low_income_credit)
