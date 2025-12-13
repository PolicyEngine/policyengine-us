from policyengine_us.model_api import *


class ok_tanf_earned_income_after_work_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma TANF earned income after work expense per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-33"
    )
    defined_for = StateCode.OK

    def formula(person, period, parameters):
        gross_earned = person("tanf_gross_earned_income", period)
        work_expense = person("ok_tanf_work_expense_person", period)
        return max_(gross_earned - work_expense, 0)
