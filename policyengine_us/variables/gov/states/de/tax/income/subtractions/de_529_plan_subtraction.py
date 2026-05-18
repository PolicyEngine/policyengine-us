from policyengine_us.model_api import *


class de_529_plan_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Delaware subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
        "https://treasurer.delaware.gov/education-savings-plan/",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions.plan_529
        contributions = person("investment_in_529_plan_indv", period)
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        # Income eligibility
        agi = person.tax_unit("adjusted_gross_income", period)
        agi_limit = p.agi_limit[filing_status]
        eligible = agi < agi_limit
        return eligible * min_(contributions, cap)
