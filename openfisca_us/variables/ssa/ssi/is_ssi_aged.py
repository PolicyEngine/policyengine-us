from openfisca_us.model_api import *


class is_ssi_aged(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is aged for the Supplemental Security Income program"
    label = "SSI aged"

    def formula(person, period, parameters):
        return person.age >= parameters(period).ssi.aged_threshold
