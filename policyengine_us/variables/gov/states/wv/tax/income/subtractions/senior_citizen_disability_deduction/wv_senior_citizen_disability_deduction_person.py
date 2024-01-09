from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_person(Variable):
    value_type = float
    entity = Person
    label = (
        "West Virginia senior citizen or disability deduction for each person"
    )
    unit = USD
    definition_period = YEAR
    defined_for = "wv_senior_citizen_disability_deduction_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        agi_person = person("adjusted_gross_income_person", period)
        capped_agi = min_(p.cap, agi_person)
        # While the legal code specifies that the total value of the modifications can not exceed
        # a certain amount, we can mathematically derive this condition by subtracting the modification
        # amount from the adjusted gross income as specified in subdivision (c) (9) (ii)
        total_modifications = person(
            "wv_senior_citizen_disability_deduction_total_modifications",
            period,
        )
        return max_(0, capped_agi - total_modifications)
