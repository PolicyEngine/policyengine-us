from policyengine_us.model_api import *


class commodity_supplemental_food_program_eligible(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Commodity Supplemental Food Program eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.csfp
        fpg = person.spm_unit("wic_fpg", period)
        age = person("age", period)

        age_eligible = age >= p.min_age
        income_eligible = fpg <= p.fpg_limit

        return age_eligible & income_eligible
