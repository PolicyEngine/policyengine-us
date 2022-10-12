from policyengine_us.model_api import *


class ca_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California standard deduction"
    unit = USD
    documentation = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
