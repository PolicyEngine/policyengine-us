from policyengine_us.model_api import *


class meets_snap_abawd_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.24"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.abawd
        age = person("monthly_age", period)
        weekly_hours_worked = person("weekly_hours_worked", period.this_year)
        # Work at least 20 hours a week
        is_working = weekly_hours_worked >= p.weekly_hours_threshold
        # Under 18 or 55 years of age or older are exempted
        worked_exempted_age = p.age_threshold.exempted.calc(age)
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Pregnant
        is_pregnant = person("is_pregnant", period)
        # Is otherwise exempt from work requirements under section 6(d)(2)
        # of the Food and Nutrition Act of 2008, as implemented in regulations at § 273.7(b)
        # This is the general work requirement https://www.law.cornell.edu/cfr/text/7/273.7#b
        has_incapacitated_person = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        # Homeless
        is_homeless = person.household("is_homeless", period)
        # A veteran
        is_veteran = person("is_veteran", period)
        return (
            is_working
            | worked_exempted_age
            | is_disabled
            | has_incapacitated_person
            | is_pregnant
            | is_homeless
            | is_veteran
        )
