from openfisca_us.model_api import *


class is_wic_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Meets the income, categorical, nutritional, and demographic eligibility criteria for WIC"
    label = "Meets WIC eligibility criteria"
    reference = "https://www.law.cornell.edu/cfr/text/7/246.7"

    def formula(person, period, parameters):
        meets_income_test = person.spm_unit("meets_wic_income_test", period)
        meets_categorical_test = person.spm_unit(
            "meets_wic_categorical_eligibility", period
        )
        wic_category = person("wic_category", period)
        wic_categories = wic_category.possible_values
        nutritional_risk = person("is_wic_at_nutritional_risk", period)
        return (
            (wic_category != wic_categories.NONE)
            & meets_income_test
            & meets_categorical_test
            & nutritional_risk
        )
