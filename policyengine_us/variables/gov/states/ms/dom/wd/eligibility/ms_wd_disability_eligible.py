from policyengine_us.model_api import *


class ms_wd_disability_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Mississippi Working Disabled disability eligible"
    definition_period = MONTH
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=31",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        is_disabled = person("is_disabled", period.this_year)
        is_blind = person("is_blind", period.this_year)
        receives_ssdi = person("social_security_disability", period) > 0
        return is_disabled | is_blind | receives_ssdi
