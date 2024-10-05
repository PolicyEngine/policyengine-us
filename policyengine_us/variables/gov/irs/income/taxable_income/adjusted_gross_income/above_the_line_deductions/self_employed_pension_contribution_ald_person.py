from policyengine_us.model_api import *


class self_employed_pension_contribution_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Self-employed pension contribution ALD for each person"
    unit = USD
    documentation = "Personal above-the-line deduction for self-employed pension plan contributions."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/162#l"

    def formula(person, period, parameters):
        earnings = max_(0, person("self_employment_income", period))
        contributions = person("self_employed_pension_contributions", period)
        return min_(earnings, contributions)
