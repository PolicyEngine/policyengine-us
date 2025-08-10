from policyengine_us.model_api import *


class il_aabd_non_financial_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD)"
    reference = "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-B"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        aged_or_blind_or_disabled = person(
            "il_aabd_aged_blind_disabled_person", period
        )
        immigration_status_eligible = person(
            "il_aabd_immigration_status_eligible_person", period
        )

        return aged_or_blind_or_disabled & immigration_status_eligible
