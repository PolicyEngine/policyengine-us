from policyengine_us.model_api import *


class is_wic_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Is eligible for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "Is eligible for WIC"
    reference: "https://www.law.cornell.edu/cfr/text/7/246.7#c_1"

    def formula(person, period, parameters):
        meets_income_test = person.spm_unit("meets_wic_income_test", period)
        meets_categorical_test = person(
            "meets_wic_categorical_eligibility", period
        )
        nutritional_risk = person("is_wic_at_nutritional_risk", period)
        return (meets_income_test | meets_categorical_test) & nutritional_risk
