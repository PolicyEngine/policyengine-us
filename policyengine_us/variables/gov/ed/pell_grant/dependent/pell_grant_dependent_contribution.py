from policyengine_us.model_api import *


class pell_grant_dependent_contribution(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant dependent contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person("pell_grant_countable_assets", period)
        simplified = person("pell_grant_simplified_formula_applies", period)
        income = person("pell_grant_dependent_available_income", period)
        allowances = person("pell_grant_dependent_allowances", period)
        p = parameters(period).gov.ed.pell_grant.dependent
        adjusted_income = (income - allowances) * p.income_assessment_rate
        adjusted_assets = assets * p.asset_assessment_rate * ~simplified
        return adjusted_income + adjusted_assets
