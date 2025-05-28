from policyengine_us.model_api import *


class il_ccap_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Illinois Child Care Assistance Program (CCAP) based on immigration status"
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=46885"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
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
