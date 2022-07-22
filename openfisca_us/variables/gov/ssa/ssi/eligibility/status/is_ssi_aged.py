from openfisca_us.model_api import *


class is_ssi_aged(Variable):
    value_type = bool
    entity = Person
    label = "Is aged for SSI"
    definition_period = YEAR

    def formula(person, period, parameters):
        aged_threshold = parameters(
            period
        ).gov.ssa.ssi.eligibility.aged_threshold
        return person("age", period) >= aged_threshold
