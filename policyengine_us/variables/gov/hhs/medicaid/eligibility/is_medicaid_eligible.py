from policyengine_us.model_api import *


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
        immigration_status_eligible = person(
            "is_medicaid_immigration_status_eligible", period
        )
        ca_ffyp_eligible = person("ca_ffyp_eligible", period)
        il_hbi_eligible = person("il_hbi_eligible", period)

        p = parameters(period).gov.hhs.medicaid.eligibility
        federal_medicaid_eligible = (
            categorically_eligible & immigration_status_eligible
        )
        if p.work_requirements.applies:
            work_requirement_eligible = person(
                "medicaid_work_requirement_eligible", period
            )
            adult_group = category == category.possible_values.ADULT
            return (
                federal_medicaid_eligible
                & (~adult_group | work_requirement_eligible)
                | ca_ffyp_eligible
                | il_hbi_eligible
            )
        return (
            federal_medicaid_eligible
            | ca_ffyp_eligible
            | il_hbi_eligible
        )
