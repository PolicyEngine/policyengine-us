from policyengine_us.model_api import *


class va_meets_filing_requirement(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit meets the Virginia income tax filing requirement"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2023-760-instructions.pdf#page=10"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("va_agi", period)
        p = parameters(period).gov.states.va.tax.income
        filing_status = tax_unit("filing_status", period)
        return agi >= p.filing_requirement[filing_status] 
