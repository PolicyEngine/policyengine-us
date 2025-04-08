from policyengine_us.model_api import *


class il_aabd_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD) based on demographics"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.30",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.40",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.50",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd
        age = person("monthly_age", period)
        elderly = age >= p.elderly_age_threshold
        blind = person("is_blind", period)
        disabled = person("is_ssi_disabled", period)
        elderly_or_blind_or_disabled = elderly | blind | disabled 
        ssi_eligible = person("is_ssi_eligible", period)
        
        return elderly_or_blind_or_disabled & ssi_eligible 
