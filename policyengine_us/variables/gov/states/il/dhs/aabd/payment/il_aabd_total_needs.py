from policyengine_us.model_api import *


class il_aabd_total_needs(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) total needs"
    unit = USD
    definition_period = MONTH
    defined_for = "il_aabd_eligible_person"

    adds = [
        "il_aabd_grant_amount",
        "il_aabd_utility_allowance",
        "il_aabd_personal_allowance",
        "il_aabd_shelter_allowance",
    ]
