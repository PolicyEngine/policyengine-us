from policyengine_us.model_api import *


class va_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        return p.standard[filing_status]
