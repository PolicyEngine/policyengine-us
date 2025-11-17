from policyengine_us.model_api import *


class il_hbwd_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities immigration status eligible"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I03100R.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd
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
