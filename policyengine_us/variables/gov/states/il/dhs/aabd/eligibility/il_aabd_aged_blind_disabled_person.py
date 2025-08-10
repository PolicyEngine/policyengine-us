from policyengine_us.model_api import *


class il_aabd_aged_blind_disabled_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Aged, blind, or disabled person for Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.30",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.40",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.50",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd
        age = person("monthly_age", period)
        is_aged = age >= p.aged_age_threshold
        is_blind = person("is_blind", period)
        is_disabled = person("is_ssi_disabled", period)
        return is_aged | is_blind | is_disabled
