from policyengine_us.model_api import *


class is_wic_at_nutritional_risk(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "At nutritional risk for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b_8"

    def formula(person, period, parameters):
        # Assign households WIC nutritional risk status probabilistically in microsimulation.
        # Assume all meet qualification in individual simulation.
        if hasattr(person.simulation, "dataset"):
            wic_reported = person("receives_wic", period)
            meets_income_test = person.spm_unit(
                "meets_wic_income_test", period
            )
            meets_categorical_test = person(
                "meets_wic_categorical_eligibility", period
            )
            category = person("wic_category", period)
            risk = parameters(period).gov.usda.wic.nutritional_risk
            imputed_risk = (random(person) < risk[category]) & (
                meets_income_test | meets_categorical_test
            )
            return wic_reported | imputed_risk
        else:
            return True
