from policyengine_us.model_api import *


class dc_ccsp_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for DC Child Care Subsidy Program (CCSP) based on immigration status"
    definition_period = MONTH
    reference = ""
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.qualified_alien_statuses,
        )
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        
        return has_qualifying_status | is_citizen
