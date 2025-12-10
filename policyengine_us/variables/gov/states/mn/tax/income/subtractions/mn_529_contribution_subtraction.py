from policyengine_us.model_api import *


class mn_529_contribution_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota 529 Plan Contribution Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.23",
        "https://www.revenue.state.mn.us/education-savings-account-contribution-subtraction",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.tax.income.subtractions.education_savings
        # Get 529 contributions
        contributions = tax_unit("investment_in_529_plan", period)
        # Get filing status for maximum limit
        filing_status = tax_unit("filing_status", period)
        max_subtraction = p.cap[filing_status]
        # Subtraction is lesser of contributions or maximum
        return min_(contributions, max_subtraction)
