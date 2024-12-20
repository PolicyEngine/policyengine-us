from policyengine_us.model_api import *


class la_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
