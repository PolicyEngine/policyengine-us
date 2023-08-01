from policyengine_us.model_api import *


class pell_grant_parent_contribution(Variable):
    value_type = float
    entity = Person
    label = "Parent Contribution"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        assets = spm_unit("pell_grant_parent_assets", period)
        allowances = spm_unit("pell_grant_parent_allowances", period)
        income = spm_unit("pell_grant_parent_income", period)
        ajusted_assets = assets * .12
        ajusted_income = income - allowances
        available_income = ajusted_income + ajusted_assets
        p = parameters(period)
        base = p.base.calc(available_income)
        percent = p.percent.calc(available_income)
        return base + ((available_income - base) * percent)
