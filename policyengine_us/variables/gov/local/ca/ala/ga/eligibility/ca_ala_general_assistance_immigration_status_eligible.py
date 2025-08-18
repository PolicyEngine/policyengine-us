from policyengine_us.model_api import *


class ca_ala_general_assistance_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Alameda County General Assistance due to immigration status"
    definition_period = MONTH
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=21"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(immigration_status_str, p.qualified_immigration_status)
