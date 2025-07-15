from policyengine_us.model_api import *


class wic(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    documentation = "Benefit value for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "WIC"
    reference = (
        "https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/7/246.7",
    )
    unit = USD
    exhaustive_parameter_dependencies = "gov.usda.wic"
    defined_for = "is_wic_eligible"

    def formula(person, period, parameters):
        category = person("wic_category_str", period)
        p = parameters(period).gov.usda.wic
        values = p.value
        value_if_eligible = values[category]
        would_takeup = person("would_claim_wic", period)
        if p.abolish_wic:
            return 0
        return would_takeup * value_if_eligible
