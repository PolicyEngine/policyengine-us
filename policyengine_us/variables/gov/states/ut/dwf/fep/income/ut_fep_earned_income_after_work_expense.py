from policyengine_us.model_api import *


class ut_fep_earned_income_after_work_expense(Variable):
    value_type = float
    entity = Person
    label = "Utah TANF earned income after work expense deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(person, period, parameters):
        # $100 work expense deduction per employed person
        p = parameters(period).gov.states.ut.dwf.fep.income.deductions
        earned_income = person("tanf_gross_earned_income", period)
        return max_(earned_income - p.work_expense_allowance.amount, 0)
