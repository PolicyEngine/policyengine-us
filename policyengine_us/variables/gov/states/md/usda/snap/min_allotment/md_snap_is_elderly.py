from policyengine_us.model_api import *


class md_snap_is_elderly(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is an elderly person for Maryland SNAP minimum allotment"
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.usda.snap.min_allotment
        return person("age", period) >= p.age_threshold
