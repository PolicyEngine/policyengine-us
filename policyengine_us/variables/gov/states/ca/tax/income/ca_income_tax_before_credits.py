from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class ca_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA income tax before credits"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("ca_taxable_income", period)
        p = parameters(period).gov.states.ca.tax.income.rates

        return select_filing_status_value(filing_status, p, taxable_income)
