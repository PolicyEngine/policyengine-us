from policyengine_us.model_api import *


class dc_tanf_is_working(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Person is working under DC Temporary Assistance for Needy Families (TANF)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19b#(b)"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.age_threshold
        weekly_hours_worked = person("weekly_hours_worked", period)
        age = person("monthly_age", period)
        has_child_under_6 = person.spm_unit.any(age < 6)
        single_parent_requirement = where(
            has_child_under_6,
            weekly_hours_worked > 20,
            weekly_hours_worked > 30,
        )
        two_parents_requirement = weekly_hours_worked > 35
        return single_parent_requirement | two_parents_requirement
