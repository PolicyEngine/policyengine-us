from policyengine_us.model_api import *


class wic_if_takes_up(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    documentation = (
        "Benefit value for the Special Supplemental Nutrition Program for "
        "Women, Infants and Children (WIC) the person would receive if they "
        "take up the program, regardless of reported take-up."
    )
    label = "WIC if takes up"
    reference = (
        "https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/7/246.7",
        "https://www.law.cornell.edu/cfr/text/7/246.10",
        "https://www.fns.usda.gov/wic/food-packages",
    )
    unit = USD
    exhaustive_parameter_dependencies = "gov.usda.wic"
    defined_for = "is_wic_eligible"

    def formula(person, period, parameters):
        food_package = person("wic_food_package_str", period)
        p = parameters(period).gov.usda.wic
        base_value = p.value[food_package]
        current_cvb = p.cvb.current[food_package]
        included_cvb = p.cvb.included_in_value[food_package]
        cvb_adjustment = p.cvb.replaces_included_value * (current_cvb - included_cvb)
        if p.abolish_wic:
            return 0
        return max_(0, base_value + cvb_adjustment)
