from policyengine_us.model_api import *


class tx_ccs_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Texas Child Care Services based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-41"
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.qualified_immigration_statuses,
        )
