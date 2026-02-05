from policyengine_us.model_api import *


class is_wic_at_nutritional_risk(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    documentation = "Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "At nutritional risk for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b_8"

    def formula(person, period, parameters):
        draw = person("wic_nutritional_risk_draw", period)
        wic_reported = person("receives_wic", period)
        category = person("wic_category", period)
        risk = parameters(period).gov.usda.wic.nutritional_risk
        imputed_risk = draw < risk[category]
        return wic_reported | imputed_risk
