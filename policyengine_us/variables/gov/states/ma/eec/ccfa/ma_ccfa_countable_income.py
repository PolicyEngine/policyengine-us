from policyengine_us.model_api import *


class ma_ccfa_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts Child Care Financial Assistance (CCFA) countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=39",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=22",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.income.countable_income
        income = add(spm_unit, period, ["ma_ccfa_countable_income_person"])
        person = spm_unit.members
        parent = person("ma_ccfa_is_parent", period.this_year)
        deductions = add(person, period, p.deductions)
        return max_(income - spm_unit.sum(parent * deductions), 0)
