from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    label = "SSI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382"

    def formula(person, period, parameters):
        return max_(0, person("uncapped_ssi", period))
