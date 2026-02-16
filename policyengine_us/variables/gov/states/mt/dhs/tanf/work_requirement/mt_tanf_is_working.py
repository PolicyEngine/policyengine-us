from policyengine_us.model_api import *


class mt_tanf_is_working(Variable):
    value_type = bool
    entity = Person
    label = "Person is working under the work requirement for Montana Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF705.1.pdf#page=1"
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.dhs.tanf.work_requirement.required_hours
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        age = person("monthly_age", period)
        is_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period.this_year
        )
        is_disabled = person("is_disabled", period.this_year)
        spm_unit = person.spm_unit
        is_youngest_member = person.get_rank(spm_unit, age, spm_unit) == 0
        youngest_age = spm_unit.sum(is_youngest_member * age)

        able_parents = is_head_or_spouse & ~is_disabled
        is_two_parent_unit = spm_unit.sum(able_parents) > 1
        # For single parent with a child under 6, work 27 hours per week
        # For single parent with a child at 6 or older, work 33 hours per week
        # For two-parent household, work-eligible heads of the household must individually meet the 33-hour/week requirement
        required_hours = where(
            is_two_parent_unit,
            p.two_parents.amount,
            p.single_parent.amount.calc(youngest_age),
        )
        return is_head_or_spouse & (weekly_hours_worked >= required_hours)
