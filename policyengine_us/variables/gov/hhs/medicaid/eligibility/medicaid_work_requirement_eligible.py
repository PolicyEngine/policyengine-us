from policyengine_us.model_api import *


class medicaid_work_requirement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Medicaid via work requirement"
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        # Works no less than 80 hours p.680 (2)(A)
        monthly_hours_worked = person("monthly_hours_worked", period)
        meets_monthly_work_hours = (
            monthly_hours_worked >= p.monthly_hours_threshold
        )
        # The individual is enrolled in an educational program at least half-time. p.680 (2)(D)
        is_full_time_student = person("is_full_time_student", period)
        # pregnant or postpartum medical assistance p.681 (3)(A)(i)(II)(bb)
        is_pregnant = person("is_pregnant", period)
        # Has attained age of 19 and is under 65 is require to work p.693 (bb)
        age = person("age", period)
        work_required_age = p.age_range.calc(age)
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
        # parent, guardian, caretaker of a dependent child 13 years of age or under  p.694 (III)
        child_age_eligible = age <= p.dependent_age_limit
        has_eligible_dependent_child = person.tax_unit.any(
            is_dependent & child_age_eligible
        )
        exempted_from_work = (
            is_full_time_student
            | is_pregnant
            | has_disabled
            | eligible_veteran
            | eligible_disabled
        )
        meets_base_requirement = meets_monthly_work_hours | exempted_from_work
        meets_conditions = (
            meets_base_requirement | has_eligible_dependent_child
        )
        return where(work_required_age, meets_conditions, True)
