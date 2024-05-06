from policyengine_us.model_api import *


class al_retirement_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Alabama retirement exemption"
    # Schedule RS Part II & III Line 10
    documentation = "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        age = person("age", period)
        eligible_age = age >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_age & head_or_spouse
