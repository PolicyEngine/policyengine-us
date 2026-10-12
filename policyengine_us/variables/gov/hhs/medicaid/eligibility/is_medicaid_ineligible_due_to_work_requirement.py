from policyengine_us.model_api import *


class is_medicaid_ineligible_due_to_work_requirement(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible for Medicaid due to a work requirement"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        category = person("medicaid_category", period)
        federal_medicaid_eligible = (
            category != category.possible_values.NONE
        ) & person("is_medicaid_immigration_status_eligible", period)

        federal_barred = False
        p = parameters(period).gov.hhs.medicaid.eligibility.work_requirements
        if p.applies:
            applicable_adult = person(
                "is_medicaid_work_requirement_applicable_adult", period
            )
            work_requirement_eligible = person(
                "medicaid_work_requirement_eligible", period
            )
            federal_barred = (
                federal_medicaid_eligible
                & applicable_adult
                & ~work_requirement_eligible
            )

        ar_barred = False
        ar_p = parameters(period).gov.states.ar.dhs.medicaid.work_requirements
        if ar_p.applies:
            in_ar = person.household("state_code_str", period) == "AR"
            ar_barred = (
                in_ar
                & federal_medicaid_eligible
                & ~person("ar_medicaid_work_requirement_eligible", period)
            )

        return federal_barred | ar_barred
