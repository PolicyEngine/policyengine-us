from policyengine_us.model_api import *


class pell_grant_contribution_from_assets(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant head contribution from assets"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person.tax_unit("pell_grant_head_assets", period)
        simplified = person("pell_grant_simplified_formula_applies", period)
        formula = person("pell_grant_formula", period)
        p = parameters(period).gov.ed.pell_grant.head
        return assets * p.asset_assessment_rate[formula] * ~simplified
