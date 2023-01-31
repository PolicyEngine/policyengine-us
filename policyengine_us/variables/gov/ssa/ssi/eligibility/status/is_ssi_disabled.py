from policyengine_us.model_api import *


class is_ssi_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is disabled for the Supplemental Security Income program"
    label = "SSI disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"

    def formula(person, period, parameters):
        aged = person("is_ssi_aged", period)
        blind = person("is_blind", period)
        reported_receipt = person("ssi_reported", period) > 0
        return reported_receipt & ~aged & ~blind
