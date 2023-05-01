from policyengine_us.model_api import *


class dc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
