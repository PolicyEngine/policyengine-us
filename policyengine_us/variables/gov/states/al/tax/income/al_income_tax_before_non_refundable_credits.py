from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class al_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama income tax before non-refundable credits"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    # The Code of Alabama 1975 Section 40-18-5
    reference = " https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("al_taxable_income", period)
        p = parameters(period).gov.states.al.tax.income.rates

        return select_filing_status_value(filing_status, p, taxable_income)
