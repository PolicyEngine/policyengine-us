from policyengine_us.model_api import *


class ca_wdp_disability_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program disability eligible"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)
        receives_ssdi = person("social_security_disability", period) > 0
        return is_disabled | is_blind | receives_ssdi
