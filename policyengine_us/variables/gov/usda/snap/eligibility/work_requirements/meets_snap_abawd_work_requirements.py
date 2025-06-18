from policyengine_us.model_api import *


class meets_snap_abawd_work_requirements(Variable):  # This one get a reform
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.24"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        age = person("monthly_age", period)
        weekly_hours_worked = person(
            "weekly_hours_worked_before_lsr", period.this_year
        )
        # Too old or too young can exempted from working
        worked_exempted_age = p.age_threshold.work_exempted.calc(age)
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Work at least 20 hours a week
        is_working = weekly_hours_worked >= p.weekly_hours_threshold
        # Pregnant
        is_pregnant = person("is_pregnant", period)
        # A veteran
        is_veteran = person("is_veteran", period)
        # Homeless
        is_homeless = person.household("is_homeless", period)
        # Parent of a household member under 18
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age < p.age_threshold.dependent
        is_parent = person("is_parent", period)
        has_child = person.spm_unit.any(is_dependent & is_child)
        exempted_parent = is_parent & has_child
        return (
            worked_exempted_age
            | is_working
            | is_disabled
            | is_pregnant
            | is_veteran
            | is_homeless
            | exempted_parent
        )
