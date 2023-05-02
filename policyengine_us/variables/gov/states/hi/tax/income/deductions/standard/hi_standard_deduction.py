from policyengine_us.model_api import *


class hi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii standard deduction"
    unit = USD
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
