from policyengine_us.model_api import *


class dc_ccsp_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for DC Child Care Subsidy Program (CCSP) based on immigration status"
    definition_period = MONTH
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8"
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.qualified_immigration_statuses,
        )
