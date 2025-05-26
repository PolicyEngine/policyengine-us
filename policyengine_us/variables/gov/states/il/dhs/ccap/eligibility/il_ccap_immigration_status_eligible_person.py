from policyengine_us.model_api import *


class il_ccap_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Illinois Child Care Assistance Program (CCAP) based on immigration status"
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=46885"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        return qualified_noncitizen | is_citizen
