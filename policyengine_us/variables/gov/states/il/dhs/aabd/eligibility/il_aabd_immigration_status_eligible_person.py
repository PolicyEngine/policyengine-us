from policyengine_us.model_api import *


class il_aabd_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD) based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.10"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd
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
