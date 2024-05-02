from policyengine_us.model_api import *


class pell_grant_head_available_income(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant head available income"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person.tax_unit("pell_grant_head_assets", period)
        simplified = person("pell_grant_simplified_formula_applies", period)
        allowances = person("pell_grant_head_allowances", period)
        income = person.tax_unit("pell_grant_primary_income", period)
        formula = person("pell_grant_formula", period)
        p = parameters(period).gov.ed.pell_grant.efc.head
        adjusted_assets = (
            assets * p.asset_assessment_rate[formula] * ~simplified
        )
        adjusted_income = (income - allowances) * p.income_assessment_rate[
            formula
        ]
        return adjusted_income + adjusted_assets
