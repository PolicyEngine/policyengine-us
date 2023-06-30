from policyengine_us.model_api import *


class la_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.la.tax.income.deductions.standard
        return p.amount[filing_status]
