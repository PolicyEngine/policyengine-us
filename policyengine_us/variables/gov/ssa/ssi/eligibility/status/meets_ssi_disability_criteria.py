from policyengine_us.model_api import *


class meets_ssi_disability_criteria(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person meets the Supplemental Security Income disability criteria"
    label = "Meets SSI disability criteria"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"

    def formula(person, period, parameters):
        is_disabled = person("is_disabled", period)
        engaged_in_sga = person("ssi_engaged_in_sga", period)
        return is_disabled & ~engaged_in_sga
