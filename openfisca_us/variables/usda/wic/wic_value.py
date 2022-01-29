from openfisca_us.model_api import *


class wic_value(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Average benefit value for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "WIC value"
    reference = "https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2"

    def formula(person, period, parameters):
        values = parameters(period).usda.wic.value
        category = person("wic_category", period)
        return values[category] * 12
