from policyengine_us.model_api import *


class ca_cc_general_assistance_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Contra Costa County General Assistance due to immigration status"
    definition_period = MONTH
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.cc.general_assistance
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(immigration_status_str, p.qualified_immigration_status)
