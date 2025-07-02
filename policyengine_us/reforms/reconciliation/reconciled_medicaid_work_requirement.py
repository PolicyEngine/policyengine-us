from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_medicaid_work_requirement() -> Reform:
    class medicaid_work_requirement_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible person for Medicaid via work requirement"
        definition_period = YEAR
        reference = (
            "https://www.budget.senate.gov/imo/media/doc/the_one_big_beautiful_bill_act.pdf=678",
            "https://budget.house.gov/imo/media/doc/one_big_beautiful_bill_act_-_full_bill_text.pdf#page=364",
        )

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.medicaid_work_requirement
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
            is_incapable_of_self_care = person(
                "is_incapable_of_self_care", period
            )
            eligible_disabled = (
                is_blind | is_disabled | is_incapable_of_self_care
            )
            # House Version
            # parent, guardian, caretaker of a dependent child p.377 (III)
            # https://budget.house.gov/imo/media/doc/one_big_beautiful_bill_act_-_full_bill_text.pdf#page=377
            is_child = person("is_child", period)
            has_dependent_child_house = person.tax_unit.any(
                is_dependent & is_child
            )
            # Senate Version
            # parent, guardian, caretaker of a dependent child 13 years of age or under  p.694 (III)
            child_age_eligible = age <= p.senate.dependent_age_limit
            has_dependent_child_senate = person.tax_unit.any(
                is_dependent & child_age_eligible
            )
            exempted_from_work = (
                is_full_time_student
                | is_pregnant
                | has_disabled
                | eligible_veteran
                | eligible_disabled
            )
            meets_base_requirement = (
                meets_monthly_work_hours | exempted_from_work
            )
            meets_senate_condition = (
                meets_base_requirement | has_dependent_child_senate
            )
            meets_house_condition = (
                meets_base_requirement | has_dependent_child_house
            )
            if p.senate.in_effect:
                return where(work_required_age, meets_senate_condition, True)
            elif p.house.in_effect:
                return where(work_required_age, meets_house_condition, True)
            else:
                return True

    class is_medicaid_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible for Medicaid"
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/42/1396a#a_10"
            "https://www.kff.org/racial-equity-and-health-policy/fact-sheet/key-facts-on-health-coverage-of-immigrants"
        )

        def formula(person, period, parameters):
            category = person("medicaid_category", period)
            categorically_eligible = category != category.possible_values.NONE
            istatus = person("immigration_status", period)
            undocumented = istatus == istatus.possible_values.UNDOCUMENTED
            state = person.household("state_code_str", period)
            p = parameters(period).gov.hhs.medicaid.eligibility
            state_covers_undocumented = p.undocumented_immigrant[state].astype(
                bool
            )
            immigration_status_eligible = (
                ~undocumented | undocumented & state_covers_undocumented
            )
            work_requirement_eligible = person(
                "medicaid_work_requirement_eligible", period
            )
            ca_ffyp_eligible = person("ca_ffyp_eligible", period)
            return (
                categorically_eligible
                & immigration_status_eligible
                & work_requirement_eligible
            ) | ca_ffyp_eligible

    class reform(Reform):
        def apply(self):
            self.update_variable(medicaid_work_requirement_eligible)
            self.update_variable(is_medicaid_eligible)

    return reform


def create_reconciled_medicaid_work_requirement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_medicaid_work_requirement()

    p = parameters.gov.contrib.reconciliation.medicaid_work_requirement

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if (
            p(current_period).house.in_effect
            or p(current_period).senate.in_effect
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_medicaid_work_requirement()
    else:
        return None


reconciled_medicaid_work_requirement = (
    create_reconciled_medicaid_work_requirement_reform(None, None, bypass=True)
)
