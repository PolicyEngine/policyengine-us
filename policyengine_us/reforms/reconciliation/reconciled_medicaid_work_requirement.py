from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_medicaid_work_requirement() -> Reform:
    class medicaid_work_requirement_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible person for Medicaid via work requirement"
        unit = USD
        definition_period = YEAR
        reference = "https://budget.house.gov/imo/media/doc/one_big_beautiful_bill_act_-_full_bill_text.pdf#page=364"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.medicaid_work_requirement
            monthly_hours_worked = person(
                "monthly_hours_worked", period.this_year
            )
            is_working = monthly_hours_worked >= p.monthly_hours_threshold
            # The individual is enrolled in an educational program at least half-time.
            is_full_time_student = person("is_full_time_student", period)
            # pregnant or postpartum medical assistance p.365
            is_pregnant = person("is_pregnant", period)
            # (dd) https://www.ssa.gov/OP_Home/ssact/title19/1902.htm about income level
            ## Under age of 19 or over age of 65 p.376
            age = person("age", period)
            work_exempted_age = p.work_exempted_age_threshold.calc(age)
            ## parent of a disabled person(III)
            is_parent = person("is_parent", period)
            is_disabled = person("is_disabled", period)
            eligible_parent = is_parent & person.tax_unit.any(is_disabled)
            ## veteran and is_permanently_and_totally_disabled (IV)
            eligible_veteran = person("is_veteran", period) & person(
                "is_permanently_and_totally_disabled", period
            )
            ## blind or disabled or is_incapable_of_self_care (V)
            eligible_disabled = (
                person("is_blind", period)
                | is_disabled
                | person("is_incapable_of_self_care", period)
            )

            return (
                is_working
                | is_full_time_student
                | is_pregnant
                | work_exempted_age
                | eligible_parent
                | eligible_veteran
                | eligible_disabled
            )

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
        if p(current_period).in_effect:
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
