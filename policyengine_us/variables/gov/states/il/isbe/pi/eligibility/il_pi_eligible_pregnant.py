from policyengine_us.model_api import *


class il_pi_eligible_pregnant(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant woman eligible for Illinois PI"
    definition_period = YEAR
    reference = "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Expecting parents are eligible for PI services.
        return person("is_pregnant", period)
