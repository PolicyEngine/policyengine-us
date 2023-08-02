from policyengine_us.model_api import *


class pell_grant_dependent_contribution(Variable):
    value_type = float
    entity = Person
    label = "Dependent Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person("pell_grant_dependent_assets", period)
        income = person("pell_grant_dependent_available_income", period)
        allowances = person("pell_grant_dependent_allowances", period)
        p = parameters(period).gov.ed.pell_grant.efc.dependent
        ajusted_income = (income - allowances) * p.income_modification
        ajusted_assets = assets * p.asset_modification
        return ajusted_income + ajusted_assets
