from policyengine_us.model_api import *


class ms_wd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Mississippi Working Disabled eligible"
    definition_period = MONTH
    documentation = (
        "Eligibility for Mississippi's Working Disabled Medicaid Buy-In "
        "pathway. The model covers paid work of at least 40 monthly hours, "
        "disability without an SGA screen, marital-unit earned and unearned "
        "income tests, the higher WD resource limit, and Medicaid immigration "
        "status. Premium billing, retroactive-month processes, child "
        "allocations, and specialized income/resource exclusions lacking "
        "PolicyEngine inputs are not modeled."
    )
    reference = (
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=30",
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=31",
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        return (
            person("ms_wd_work_eligible", period)
            & person("ms_wd_disability_eligible", period)
            & person("ms_wd_income_eligible", period)
            & person("ms_wd_resource_eligible", period)
            & person("is_medicaid_immigration_status_eligible", period.this_year)
        )
