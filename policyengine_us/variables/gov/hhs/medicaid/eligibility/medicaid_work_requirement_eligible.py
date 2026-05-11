from policyengine_us.model_api import *


class medicaid_work_requirement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Medicaid via work requirement"
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        # Works no less than 80 hours p.680 (2)(A)
        monthly_hours_worked = person("monthly_hours_worked", period)
        meets_monthly_work_hours = monthly_hours_worked >= p.monthly_hours_threshold
        # Monthly income of at least federal minimum wage times 80 hours.
        monthly_income_threshold = (
            parameters(period).gov.dol.minimum_wage * p.monthly_hours_threshold
        )
        meets_monthly_income = person("earned_income", period) >= (
            monthly_income_threshold * MONTHS_IN_YEAR
        )
        # The individual is enrolled in an educational program at least half-time.
        is_enrolled_at_least_half_time = person(
            "is_full_time_student", period
        ) | person("is_part_time_college_student", period)
        # Pregnant or postpartum medical assistance.
        is_pregnant_or_postpartum = person("is_pregnant_for_medicaid_nfc", period)
        # Has attained age of 19 and is under 65 is require to work p.693 (bb)
        age = person("age", period)
        work_required_age = p.age_range.calc(age)
        # Former foster care Medicaid eligibility group.
        was_in_foster_care = person("was_in_foster_care", period)
        former_foster_care_youth = was_in_foster_care & (
            age < p.former_foster_care_age_limit
        )
        # Entitled to or enrolled in Medicare Part A or B.
        medicare_eligible = person("is_medicare_eligible", period)
        # parent, guardian, caretaker of a disabled person
        is_dependent = person("is_tax_unit_dependent", period)
        is_disabled = person("is_disabled", period)
        has_disabled = person.tax_unit.any(is_dependent & is_disabled)
        # veteran and is_permanently_and_totally_disabled p.694 (IV)
        is_veteran = person("is_veteran", period)
        is_permanently_and_totally_disabled = person(
            "is_permanently_and_totally_disabled", period
        )
        eligible_veteran = is_veteran & is_permanently_and_totally_disabled
        # blind or disabled or is_incapable_of_self_care p.694 (V)
        is_blind = person("is_blind", period)
        is_incapable_of_self_care = person("is_incapable_of_self_care", period)
        eligible_disabled = is_blind | is_disabled | is_incapable_of_self_care
        is_incarcerated = person("is_incarcerated", period)
        # parent, guardian, caretaker of a dependent child 13 years of age or under  p.694 (III)
        child_age_eligible = age <= p.dependent_age_limit
        has_eligible_dependent_child = person.tax_unit.any(
            is_dependent & child_age_eligible
        )
        exempted_from_work = (
            is_enrolled_at_least_half_time
            | is_pregnant_or_postpartum
            | former_foster_care_youth
            | medicare_eligible
            | has_disabled
            | eligible_veteran
            | eligible_disabled
            | is_incarcerated
        )
        meets_base_requirement = (
            meets_monthly_work_hours | meets_monthly_income | exempted_from_work
        )
        meets_conditions = meets_base_requirement | has_eligible_dependent_child
        return where(work_required_age, meets_conditions, True)
