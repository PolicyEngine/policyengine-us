from policyengine_us.model_api import *


class ca_ala_general_assistance_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Alameda County General Assistance due to immigration status"
    definition_period = MONTH
    defined_for = "in_ala"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_status,
        )
        return has_qualifying_status | is_citizen
