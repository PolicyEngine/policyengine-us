from policyengine_us.model_api import *


class mt_tanf_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Montana TANF based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.220"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.dhs.tanf
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_status,
        )
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )

        return has_qualifying_status | is_citizen
