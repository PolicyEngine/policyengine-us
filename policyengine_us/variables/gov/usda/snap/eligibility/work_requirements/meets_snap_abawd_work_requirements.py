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
        # Adults within an age range are exempt
        working_age_exempt = p.age_threshold.exempted.calc(age)
        # Unable to work due to a physical or mental limitation
        is_disabled = person("is_disabled", period)
        # Parent or other member of a household with responsibility for a dependent child under certain age
        is_dependent = person("is_tax_unit_dependent", period)
        is_qualifying_child = age < p.age_threshold.dependent
        is_parent = person("is_parent", period)
        has_child = person.spm_unit.any(is_dependent & is_qualifying_child)
        exempt_parent = is_parent & has_child
        # Exempted from the general work requirements
        meets_snap_general_work_requirements = person(
            "meets_snap_general_work_requirements", period
        )
        # Pregnant
        is_pregnant = person("is_pregnant", period)
        # Homeless
        is_homeless = person.household("is_homeless", period)
        # A veteran
        is_veteran = person("is_veteran", period)
        # States exempt from work requirements.
        state_code = person.household("state_code", period)
        state_code_str = state_code.decode_to_str()
        is_abawd_work_requirements_exempt_state = np.isin(
            state_code_str, p.exempt_states
        )
        base_conditions = (
            is_working
            | working_age_exempt
            | is_disabled
            | exempt_parent
            | meets_snap_general_work_requirements
            | is_pregnant
            | is_abawd_work_requirements_exempt_state
        )
        if p.in_effect:
            return base_conditions
        return base_conditions | is_homeless | is_veteran
