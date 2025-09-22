from policyengine_us.model_api import *


class mt_tanf_is_working(Variable):
    value_type = bool
    entity = Person
    label = "Person is working under the work requirement for Montana Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF705.1.pdf"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.dhs.tanf.work_requirement.required_hours
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        age = person("monthly_age", period)
        # For single parent with a child under 6, work 27 hours pr week
        # For single parent with a child at 6 or older, work 33 hours pr week
        spm_unit = person.spm_unit
        is_youngest_member = person.get_rank(spm_unit, age, spm_unit) == 0
        youngest_age = spm_unit.sum(is_youngest_member * age)
        single_parent_requirement = (
            weekly_hours_worked >= p.single_parent.amount.calc(youngest_age)
        )
        # For two-parent household, all work-eligible adults must individually meet the 33-hour/week requirement
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        two_parent_requirement = weekly_hours_worked >= p.two_parents.amount

        # Treat households with an incapacitated parent as a single parent household
        is_two_parent_unit = (spm_unit.sum(is_head_or_spouse) > 1) & (
            spm_unit.sum(person("is_incapable_of_self_care", period)) == 0
        )

        return where(
            is_two_parent_unit,
            two_parent_requirement,
            single_parent_requirement,
        )
