from policyengine_us.model_api import *


class ms_wd_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Mississippi Working Disabled income eligible"
    definition_period = MONTH
    reference = "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32"
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        return person("ms_wd_earned_income_eligible", period) & person(
            "ms_wd_unearned_income_eligible", period
        )
