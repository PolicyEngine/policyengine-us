from policyengine_us.model_api import *


class il_tanf_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Illinois TANF based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.10"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_status,
        )
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )

        return has_qualifying_status | is_citizen
