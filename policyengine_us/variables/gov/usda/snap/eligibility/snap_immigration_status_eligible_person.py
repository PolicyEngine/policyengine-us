from policyengine_us.model_api import *


class snap_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the SNAP based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.4"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str, p.qualified_immigration_statuses
        )
