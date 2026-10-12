from policyengine_us.model_api import *


class ms_wd_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Working Disabled countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32"
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.wd.eligibility.income
        unearned_income = person.marital_unit.sum(
            person("ms_wd_gross_unearned_income", period)
        )
        return max_(unearned_income - p.exclusions.general, 0)
