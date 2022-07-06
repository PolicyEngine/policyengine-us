from openfisca_us.model_api import *


class is_usda_elderly(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Is elderly per USDA guidelines"
    label = "USDA elderly"

    def formula(person, period, parameters):
        elderly_age_threshold = parameters(
            period
        ).gov.usda.elderly_age_threshold
        return person("age", period) >= elderly_age_threshold
