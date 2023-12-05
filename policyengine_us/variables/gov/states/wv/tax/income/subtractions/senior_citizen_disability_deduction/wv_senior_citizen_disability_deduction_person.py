from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "West Virginia senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "wv_senior_citizen_disability_deduction_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        wv_agi_person = person("wv_agi_person", period)
        wv_subtractions_part_two = person("wv_subtractions_part_two", period)
        income_modified = min_(p.cap, wv_agi_person - wv_subtractions_part_two)
        modification_amount = person("wv_total_modification", period)
        return max_(0, income_modified - modification_amount)

        # is_tax_unit_spouse
