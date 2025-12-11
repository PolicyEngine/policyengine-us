from policyengine_us.model_api import *


class il_hfs_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois HFS programs immigration status eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.310"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_statuses,
        )
        return has_qualifying_status | is_citizen
