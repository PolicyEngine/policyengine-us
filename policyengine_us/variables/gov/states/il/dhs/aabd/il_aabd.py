from policyengine_us.model_api import *


class il_aabd(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit"
    unit = USD
    definition_period = MONTH
    defined_for = "il_aabd_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-D",
    )

    def formula(spm_unit, period, parameters):
        grant_amount = spm_unit("il_aabd_grant_amount", period)
        supplement_payment = spm_unit("il_aabd_supplement_payment", period)
        countable_income = spm_unit("il_aabd_countable_income", period)

        return max_(grant_amount - countable_income, 0) + supplement_payment
