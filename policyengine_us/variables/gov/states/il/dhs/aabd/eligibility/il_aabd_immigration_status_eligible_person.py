from policyengine_us.model_api import *


class il_aabd_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD) based on immigration status"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.10"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        return qualified_noncitizen | is_citizen
