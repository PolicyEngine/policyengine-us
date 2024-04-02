from policyengine_us.model_api import *


class mt_disability_income_exclusion_person(Variable):
    value_type = float
    entity = Person
    label = "Montana disability income exclusion for each person"
    defined_for = "mt_disability_income_exclusion_eligible_person"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=31"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.subtractions.disability_income
        return min_(p.cap, person("disability_benefits", period))
