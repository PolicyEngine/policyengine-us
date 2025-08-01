from policyengine_us.model_api import *


class meets_snap_general_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for SNAP benefits via general work requirements"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.general
        age = person("monthly_age", period)
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        # Under 16 or 60 years of age or older are exempted
        worked_exempted_age = p.age_threshold.exempted.calc(age)
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Taking care of a child under six or an incapacitated person
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < p.age_threshold.caring_dependent_child
        has_child = person.spm_unit.any(is_dependent & is_child)
        has_incapacitated_person = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        # Work at least 30 hours a week
        is_working = weekly_hours_worked >= p.weekly_hours_threshold

        return (
            worked_exempted_age
            | is_disabled
            | has_child
            | has_incapacitated_person
            | is_working
        )
