from policyengine_us.model_api import *


class id_529_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/taxes/income-tax/individual-income/popular-credits-and-deductions/ideal-college-savings-program/",
        "https://www.idsaves.org/home/features-and-benefits/tax-benefits.html",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
