from policyengine_us.model_api import *


class pell_grant_head_available_income(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant head available income"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person.tax_unit("pell_grant_head_assets", period)
        simplified = person("pell_grant_simplified", period)
        allowances = person("pell_grant_head_allowances", period)
        income = person.tax_unit("pell_grant_head_income", period)
        formula = person("pell_grant_formula", period)
        p = parameters(period).gov.ed.pell_grant.efc.head
        ajusted_assets = assets * p.asset_modification[formula] * ~simplified
        ajusted_income = (income - allowances) * p.income_modification[formula]
        return ajusted_income + ajusted_assets
