from policyengine_us.model_api import *


class ak_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=242",
    )

    def formula(spm_unit, period):
        earned = spm_unit("ak_ccap_countable_earned_income", period)
        unearned = spm_unit("ak_ccap_countable_unearned_income", period)
        child_support_paid = spm_unit("ak_ccap_child_support_paid_deduction", period)
        return max_(0, earned + unearned - child_support_paid)
