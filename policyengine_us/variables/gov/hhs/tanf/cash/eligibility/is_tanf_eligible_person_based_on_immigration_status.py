from policyengine_us.model_api import *


class is_tanf_eligible_person_based_on_immigration_status(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Temporary Assistance for Needy Families based on immigration status"
    definition_period = MONTH

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.tanf.cash.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        return np.isin(
            immigration_status_str,
            p.qualified_immigration_statuses,
        )
