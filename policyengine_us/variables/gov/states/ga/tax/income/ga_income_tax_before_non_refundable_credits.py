from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class ga_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.main
        filing_status = tax_unit("filing_status", period)
        income = tax_unit("ga_taxable_income", period)
        return select_filing_status_value(filing_status, p, income)
