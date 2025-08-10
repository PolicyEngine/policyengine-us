from policyengine_us.model_api import *


class dc_gac_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    label = "DC General Assistance for Children (GAC) earned income after disregard per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(e)"
    )
    defined_for = "dc_gac_eligible_child"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs
        gross_earnings = person("dc_tanf_gross_earned_income", period)
        adjusted_income = max_(
            gross_earnings - p.gac.income_disregard.amount, 0
        )
        full_time_student = person("is_full_time_student", period)
        weekly_hours_worked = person("monthly_hours_worked", period)
        work_full_time = (
            weekly_hours_worked
            >= p.tanf.work_requirement.required_hours.single_parent.higher.amount
        )

        return where(work_full_time & ~full_time_student, adjusted_income, 0)
