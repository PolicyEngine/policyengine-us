from policyengine_us.model_api import *


class ca_wdp_work_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program work eligible"
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return person("ca_wdp_gross_earned_income", period) > 0
