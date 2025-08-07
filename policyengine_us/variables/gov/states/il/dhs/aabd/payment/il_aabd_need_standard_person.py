from policyengine_us.model_api import *


class il_aabd_need_standard_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) need standard for each person"
    unit = USD
    definition_period = MONTH
    defined_for = "il_aabd_non_financial_eligible_person"
    reference = "https://rockfordha.org/wp-content/uploads/2020/04/Public-Benefits-Quick-Reference-Guide-Updated.pdf#page=1"

    adds = [
        "il_aabd_grant_amount",
        "il_aabd_utility_allowance_person",
        "il_aabd_personal_allowance",
        "il_aabd_shelter_allowance",
    ]
