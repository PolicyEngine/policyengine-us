from policyengine_us.model_api import *


class is_wic_at_nutritional_risk(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    documentation = "Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "At nutritional risk for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#b_8"

    def formula(person, period, parameters):
        # Assign nutritional risk status probabilistically in microsimulation.
        # Nutritional risk is a health assessment independent of income per § 1786(b)(8).
        # Assume all meet qualification in individual simulation.
        if person.simulation.dataset is not None:
            wic_reported = person("receives_wic", period)
            category = person("wic_category", period)
            risk = parameters(period).gov.usda.wic.nutritional_risk
            imputed_risk = random(person) < risk[category]
            return wic_reported | imputed_risk
        else:
            return True
