from policyengine_us.model_api import *


class al_retirement_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Alabama retirement exemption for each person"
    unit = USD
    # Schedule RS Part II & III Line 10
    documentation = "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1"
    definition_period = YEAR
    defined_for = "al_retirement_exemption_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        retirement_income = add(
            person,
            period,
            ["taxable_retirement_distributions", "taxable_pension_income"],
        )
        return min_(retirement_income, p.cap)
