from policyengine_us.model_api import *


class ca_smc_general_assistance_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for San Mateo County General Assistance due to immigration status"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = "https://www.smcgov.org/media/153295/download?inline=#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.smc.general_assistance
        immigration_status = person("immigration_status", period.this_year)
        return np.isin(
            immigration_status.decode_to_str(),
            p.qualified_immigration_statuses,
        )
