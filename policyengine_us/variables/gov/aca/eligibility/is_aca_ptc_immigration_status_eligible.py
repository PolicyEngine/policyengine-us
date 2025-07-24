from policyengine_us.model_api import *


class is_aca_ptc_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for ACA premium tax credit and pays ACA premium due to immigration status"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.aca
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        ineligible_immigration_status = np.isin(
            immigration_status_str, p.ineligible_immigration_statuses
        )
        return ~ineligible_immigration_status
