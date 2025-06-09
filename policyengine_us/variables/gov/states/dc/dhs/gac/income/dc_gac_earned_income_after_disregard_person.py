from policyengine_us.model_api import *


class dc_gac_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "DC General Assistance to Children (GAC) earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(e)"
    )
    defined_for = "dc_gac_eligible_child"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.gac.income_disregard
        gross_earnings = person("dc_tanf_gross_earned_income", period)
        adjusted_income = max_(gross_earnings - p.amount, 0)
        full_time_student = person("is_full_time_student", period)

        return where(full_time_student, 0, adjusted_income)
