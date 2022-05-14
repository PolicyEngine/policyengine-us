from openfisca_us.model_api import *


class is_wic_at_nutritional_risk(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "At nutritional risk for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b_8"
