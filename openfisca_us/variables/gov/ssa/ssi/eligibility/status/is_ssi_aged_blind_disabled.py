from policyengine_us.model_api import *


class is_ssi_aged_blind_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is aged, blind, or disabled for the Supplemental Security Income program"
    label = "SSI aged, blind, or disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_1"

    def formula(person, period, parameters):
        return any_(
            person, period, ["is_ssi_aged", "is_blind", "is_ssi_disabled"]
        )
