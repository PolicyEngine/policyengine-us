from policyengine_us.model_api import *


class il_aabd_countable_income(Variable):
    value_type = float
    entity = Person
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) countable income"
    )
    unit = USD
    definition_period = MONTH
    defined_for = "il_aabd_non_financial_eligible_person"

    adds = [
        "il_aabd_earned_income_after_exemption_person",
        "il_aabd_countable_unearned_income",
    ]
