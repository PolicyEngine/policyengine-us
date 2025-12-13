from policyengine_us.model_api import *


class in_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4"
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        # 75% disregard per 470 IAC 10.3-4-4(d)(1)
        return spm_unit.sum(
            gross_earned * (1 - p.benefit.earned_income_disregard.rate)
        )
