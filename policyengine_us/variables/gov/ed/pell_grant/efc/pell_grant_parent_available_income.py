from policyengine_us.model_api import *


class pell_grant_parent_available_income(Variable):
    value_type = float
    entity = Person
    label = "Parent Available Income"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person("pell_grant_parent_assets", period)
        allowances = person("pell_grant_parent_allowances", period)
        income = person("pell_grant_parent_income", period)
        p = parameters(period).gov.ed.pell_grant.efc.parent
        ajusted_assets = assets * p.asset_modification
        ajusted_income = income - allowances
        return ajusted_income + ajusted_assets
