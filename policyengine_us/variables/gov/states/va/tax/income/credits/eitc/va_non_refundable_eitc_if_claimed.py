from policyengine_us.model_api import *


class va_non_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia non-refundable EITC if claimed"
    unit = USD
    documentation = (
        "Non-refundable EITC credit reducing Virginia State income tax."
    )
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.va.tax.income.credits.eitc.match
        low_income_tax_credit = tax_unit("va_low_income_tax_credit", period)
        eitc = p.non_refundable * federal_eitc
        return max_(eitc, low_income_tax_credit)
