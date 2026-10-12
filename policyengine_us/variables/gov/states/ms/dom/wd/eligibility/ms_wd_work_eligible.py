from policyengine_us.model_api import *


class ms_wd_work_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Mississippi Working Disabled work eligible"
    definition_period = MONTH
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=30",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.wd.eligibility.work
        return person("monthly_hours_worked", period.this_year) >= p.monthly_hours
