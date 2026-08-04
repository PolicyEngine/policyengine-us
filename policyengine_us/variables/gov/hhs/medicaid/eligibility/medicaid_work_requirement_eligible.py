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
        # Works or participates in qualifying activities no less than 80 hours.
        activity_hours = person("medicaid_community_engagement_activity_hours", period)
        meets_monthly_activity_hours = activity_hours >= p.monthly_hours_threshold
        # Monthly income of at least federal minimum wage times 80 hours.
        monthly_income_threshold = (
            parameters(period).gov.dol.minimum_wage * p.monthly_hours_threshold
        )
        meets_monthly_income = person("medicaid_household_income", period) >= (
            monthly_income_threshold * MONTHS_IN_YEAR
        )
        seasonal_worker = person(
            "is_medicaid_community_engagement_seasonal_worker", period
        )
        six_month_average_income = person(
            "medicaid_community_engagement_six_month_average_income", period
        )
        meets_seasonal_worker_income = seasonal_worker & (
            six_month_average_income >= monthly_income_threshold
        )
        # The individual is enrolled in an educational program at least half-time.
        is_enrolled_at_least_half_time = person(
            "is_full_time_student", period
        ) | person("is_part_time_college_student", period)
        pass_through_eligible = person(
            "medicaid_community_engagement_pass_through_eligible",
            period.first_month,
        )
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
        # American Indian or Alaska Native / IHS eligibility exclusion.
        is_aian_exempt = person(
            "is_american_indian_or_alaska_native_for_medicaid_ce", period
        )
        has_ihs_coverage = person(
            "has_indian_health_service_coverage_at_interview", period
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
        medically_frail = person(
            "is_medically_frail_or_has_special_medical_needs_for_medicaid_ce",
            period,
        )
        treatment_program_participant = person(
            "is_in_medicaid_community_engagement_treatment_program", period
        )
        # Current and recent incarceration exclusions/exceptions.
        is_incarcerated = person("is_incarcerated", period)
        was_recently_incarcerated = person(
            "was_recently_incarcerated_for_medicaid_ce", period
        )
        # parent, guardian, caretaker of a dependent child 13 years of age or under  p.694 (III)
        child_age_eligible = age <= p.dependent_age_limit
        has_eligible_dependent_child = person.tax_unit.any(
            is_dependent & child_age_eligible
        )
        exempted_from_work = (
            is_enrolled_at_least_half_time
            | pass_through_eligible
            | is_pregnant_or_postpartum
            | former_foster_care_youth
            | is_aian_exempt
            | has_ihs_coverage
            | medicare_eligible
            | has_disabled
            | eligible_veteran
            | eligible_disabled
            | medically_frail
            | treatment_program_participant
            | is_incarcerated
            | was_recently_incarcerated
        )
        meets_base_requirement = (
            meets_monthly_activity_hours
            | meets_monthly_income
            | meets_seasonal_worker_income
            | exempted_from_work
        )
        meets_conditions = meets_base_requirement | has_eligible_dependent_child
        return where(work_required_age, meets_conditions, True)
