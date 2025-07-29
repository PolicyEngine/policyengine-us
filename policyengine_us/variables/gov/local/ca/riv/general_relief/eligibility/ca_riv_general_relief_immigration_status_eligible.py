from policyengine_us.model_api import *


class ca_riv_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Riverside County General Relief due to immigration status"
    definition_period = MONTH
    defined_for = "in_riv"
    # p.40

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        return ~undocumented
