from policyengine_us.model_api import *


class is_ssi_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is disabled for the Supplemental Security Income program"
    label = "SSI disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"
