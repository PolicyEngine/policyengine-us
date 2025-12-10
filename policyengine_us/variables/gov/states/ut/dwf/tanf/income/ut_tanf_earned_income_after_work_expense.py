from policyengine_us.model_api import *


class ut_tanf_earned_income_after_work_expense(Variable):
    value_type = float
    entity = Person
    label = "Utah TANF earned income after work expense deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(person, period, parameters):
        # $100 work expense deduction per employed person
        p = parameters(period).gov.states.ut.dwf.tanf.income.deductions
        earned_income = person("tanf_gross_earned_income", period)
        return max_(earned_income - p.work_expense_allowance.amount, 0)
