from policyengine_us.model_api import *


class il_aabd_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD)"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        financial_eligible = person(
            "il_aabd_financial_eligible_person", period
        )
        non_financial_eligible = person(
            "il_aabd_non_financial_eligible_person", period
        )
        return financial_eligible & non_financial_eligible
