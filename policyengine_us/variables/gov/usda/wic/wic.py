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
        "https://www.law.cornell.edu/cfr/text/7/246.10",
        "https://www.fns.usda.gov/wic/food-packages",
    )
    unit = USD
    exhaustive_parameter_dependencies = "gov.usda.wic"
    defined_for = "takes_up_wic_if_eligible"
    adds = ["wic_if_takes_up"]
