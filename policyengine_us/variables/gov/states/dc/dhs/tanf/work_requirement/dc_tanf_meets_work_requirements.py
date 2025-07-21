from policyengine_us.model_api import *


class dc_tanf_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets work requirement for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19b"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.work_requirement.required_hours
        person = spm_unit.members
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        age = person("monthly_age", period)
        # For single parent with a child under 6, work 20 hours pr week
        # For single parent with a child at 6 or older, work 30 hours pr week
        is_child = person("is_child", period)
        is_youngest_child = person.get_rank(spm_unit, age, is_child) == 0
        youngest_age = spm_unit.sum(is_youngest_child * age)
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
        is_working = where(
            is_two_parent_unit,
            two_parent_requirement,
            single_parent_requirement,
        )
        return spm_unit.sum(is_head_or_spouse & (~is_working)) == 0
