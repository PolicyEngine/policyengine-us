from policyengine_us.model_api import *


class is_wic_at_nutritional_risk(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    documentation = "Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "At nutritional risk for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b_8"

    def formula(person, period, parameters):
        wic_reported = person("receives_wic", period)
        imputed_risk = person("wic_nutritional_risk_imputed", period)
        category = person("wic_category", period)
        has_wic_category = category != category.possible_values.NONE
        return wic_reported | (imputed_risk & has_wic_category)
