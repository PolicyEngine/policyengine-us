from policyengine_us.model_api import *


class az_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "Arizona TANF earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        # Step 1: Get person's gross earned income
        gross_earned = person("tanf_gross_earned_income", period)

        # Step 2: Apply $90 flat disregard, then 30% percentage disregard
        p = parameters(period).gov.states.az.hhs.tanf.income.deductions
        after_flat = max_(gross_earned - p.flat, 0)
        after_percentage = after_flat * (1 - p.percentage)

        return max_(after_percentage, 0)
