from policyengine_us.model_api import *


class is_co_denver_dhs_elderly(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Is elderly per Denver DHS guidelines"
    label = "Denver DHS elderly"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.co.denver.dhs
        return person("age", period) >= p.elderly_age_threshold
