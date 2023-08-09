from policyengine_us.model_api import *


class va_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware refundable EITC if claimed"
    unit = USD
    documentation = (
        "Refundable EITC credit reducing VA State income tax page 26."
    )
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=26"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.va.tax.income.credits.eitc
        return p.refundable * federal_eitc
