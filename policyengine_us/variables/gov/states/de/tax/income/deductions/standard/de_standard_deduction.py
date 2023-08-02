from policyengine_us.model_api import *


class de_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://delcode.delaware.gov/title30/c011/sc02/index.html title 30, chapter 11, subchapter II, section 1108"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.de.tax.income.deductions
        return p.standard[filing_status]
