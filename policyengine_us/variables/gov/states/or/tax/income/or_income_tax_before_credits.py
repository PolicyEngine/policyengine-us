from policyengine_us.model_api import *


class or_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.037
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        income = tax_unit("or_taxable_income", period)
        rates = parameters(period).gov.states["or"].tax.income.rates

        return select_filing_status_value(filing_status, rates, income)
