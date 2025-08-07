from policyengine_us.model_api import *


class co_income_qualified_senior_housing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Income Qualified Senior Housing Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17",
    )
    defined_for = "co_income_qualified_senior_housing_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.income_qualified_senior_housing
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        max_amount = p.reduction.max_amount[filing_status]
        reduction_start = p.reduction.start
        increment = p.reduction.increment
        reduction_amount = p.reduction.amount[filing_status]
        excess = max_(agi - reduction_start, 0)
        increments = np.where(increment > 0, np.ceil(excess / increment), 0)
        total_reduction_amount = increments * reduction_amount
        return max_(max_amount - total_reduction_amount, 0)
