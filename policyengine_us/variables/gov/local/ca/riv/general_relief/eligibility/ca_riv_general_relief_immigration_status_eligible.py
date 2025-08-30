from policyengine_us.model_api import *


class ca_riv_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Riverside County General Relief due to immigration status"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(immigration_status_str, p.qualified_immigration_status)
