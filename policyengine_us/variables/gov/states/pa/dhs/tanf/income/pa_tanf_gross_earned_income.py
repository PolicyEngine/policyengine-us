from policyengine_us.model_api import *


class pa_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF gross earned income"
    documentation = "Total gross earned income (wages, tips, salary, commissions, bonuses, self-employment) for the SPM unit before any deductions."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code § 183.21, § 183.22"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Count employment income and self-employment income
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        return spm_unit.sum(employment_income + self_employment_income)
