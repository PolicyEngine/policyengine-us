from policyengine_us.model_api import *


class wic(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Benefit value for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "WIC"
    reference = (
        "https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/7/246.7",
    )
    unit = USD

    def formula(person, period, parameters):
        meets_income_test = person.spm_unit("meets_wic_income_test", period)
        meets_categorical_test = person(
            "meets_wic_categorical_eligibility", period
        )
        category = person("wic_category_str", period)
        nutritional_risk = person("is_wic_at_nutritional_risk", period)
        eligible = (
            meets_income_test | meets_categorical_test
        ) & nutritional_risk
        p = parameters(period).gov.usda.wic
        values = p.value
        value_if_eligible = values[category]
        would_takeup = person("would_claim_wic", period)
        if p.abolish_wic:
            return 0
        return would_takeup * eligible * value_if_eligible * MONTHS_IN_YEAR
