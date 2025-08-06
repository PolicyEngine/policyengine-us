from policyengine_us.model_api import *


class dc_tanf_is_working(Variable):
    value_type = bool
    entity = Person
    label = "Person is working under the work requirement for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19b"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.work_requirement.required_hours
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        age = person("monthly_age", period)
        # For single parent with a child under 6, work 20 hours pr week
        # For single parent with a child at 6 or older, work 30 hours pr week
        spm_unit = person.spm_unit
        is_youngest_member = person.get_rank(spm_unit, age, spm_unit) == 0
        youngest_age = spm_unit.sum(is_youngest_member * age)
        single_parent_requirement = (
            weekly_hours_worked >= p.single_parent.amount.calc(youngest_age)
        )
        # For 2-parent, work 35 hours pr week (combined)
        # Or 55 hours per week if family receives federally-funded childcare and
        # no adult has a disability (not modeled)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        parent_hours = where(is_head_or_spouse, weekly_hours_worked, 0)
        combined_parent_hours = spm_unit.sum(parent_hours)
        two_parent_requirement = combined_parent_hours >= p.two_parents.amount
        is_two_parent_unit = spm_unit.sum(is_head_or_spouse) > 1
        return where(
            is_two_parent_unit,
            two_parent_requirement,
            single_parent_requirement,
        )
