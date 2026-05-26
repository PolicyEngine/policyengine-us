from policyengine_us.model_api import *


class ca_wdp_premium(Variable):
    value_type = float
    entity = Person
    label = "California 250 Percent Working Disabled Program monthly premium"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.wdp.premium
        eligible = person("ca_wdp_eligible", period.this_year)
        return eligible * p.amount
