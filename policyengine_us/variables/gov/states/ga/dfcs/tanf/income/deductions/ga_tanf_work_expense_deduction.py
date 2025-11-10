from policyengine_us.model_api import *


class ga_tanf_work_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF work expense deduction"
    unit = USD
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/1615/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.income.deductions
        person = spm_unit.members
        # Use federal TANF gross earned income variable
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        has_earned_income = gross_earned > 0
        return where(has_earned_income, p.work_expense, 0)
