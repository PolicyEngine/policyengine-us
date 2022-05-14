from openfisca_us.model_api import *


class is_ssi_aged_blind_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is aged, blind, or disabled for the Supplemental Security Income program"
    label = "SSI aged, blind, or disabled"

    def formula(person, period, parameters):
        aged_threshold = parameters(period).ssa.ssi.eligibility.aged_threshold
        aged = person("age", period) >= aged_threshold
        return any_(person, period, ["is_blind", "is_ssi_disabled"]) | aged
