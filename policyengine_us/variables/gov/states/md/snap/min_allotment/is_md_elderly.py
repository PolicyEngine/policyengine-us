from policyengine_us.model_api import *


class is_md_elderly(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Maryland elderly"
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.snap.min_allotment
        return person("age", period) >= p.age_threshold
