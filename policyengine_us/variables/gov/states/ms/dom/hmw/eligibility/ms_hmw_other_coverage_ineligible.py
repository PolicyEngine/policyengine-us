from policyengine_us.model_api import *


class ms_hmw_other_coverage_ineligible(Variable):
    value_type = bool
    entity = Person
    label = "Not otherwise eligible for Medicaid or CHIP under the Healthier Mississippi Waiver"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=9",
        "https://medicaid.ms.gov/wp-content/uploads/2022/07/Healthier-Mississippi-Waiver-Full-Public-Notice-Website.pdf#page=2",
    )

    def formula(person, period, parameters):
        other_coverage_categories = [
            "is_ssi_recipient_for_medicaid",
            "is_infant_for_medicaid",
            "is_young_child_for_medicaid",
            "is_older_child_for_medicaid",
            "is_pregnant_for_medicaid",
            "is_parent_for_medicaid",
            "is_young_adult_for_medicaid",
            "is_adult_for_medicaid",
            "is_optional_senior_or_disabled_for_medicaid",
            "is_medically_needy_for_medicaid",
            "is_working_disabled_buy_in_for_medicaid",
        ]
        state_code = person.household("state_code", period)
        age = person("age", period)
        p = parameters(period).gov.hhs.chip.child
        income_limit = p.income_limit[state_code]
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        potentially_chip_child_eligible = (
            (age < p.max_age)
            & (income_limit > 0)
            & ~undocumented
            & (person("medicaid_income_level", period) <= income_limit)
            & ~person("has_esi", period)
        )
        return (add(person, period, other_coverage_categories) == 0) & (
            ~potentially_chip_child_eligible
        )
