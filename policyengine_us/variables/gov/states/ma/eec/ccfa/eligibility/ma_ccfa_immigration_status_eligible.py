from policyengine_us.model_api import *


class ma_ccfa_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Immigration status eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=26"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.qualified_immigration_statuses,
        )
