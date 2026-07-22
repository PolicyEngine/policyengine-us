from policyengine_us.model_api import *


class is_ssi_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is disabled for the Supplemental Security Income program"
    label = "SSI disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A"

    def formula(person, period, parameters):
        # Classify person as disabled for SSI from disability inputs, not reported
        # SSI receipt. Reported SSI can inform take-up data construction, but should
        # not override calculated eligibility.
        is_disabled = person("is_disabled", period)
        engaged_in_ssa = person("ssi_engaged_in_sga", period)
        return is_disabled & ~engaged_in_ssa
