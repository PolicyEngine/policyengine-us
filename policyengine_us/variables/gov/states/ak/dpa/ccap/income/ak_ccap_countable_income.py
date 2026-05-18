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
    )

    def formula(spm_unit, period):
        return max_(
            0,
            spm_unit("ak_ccap_countable_earned_income", period)
            + spm_unit("ak_ccap_countable_unearned_income", period)
            - add(spm_unit, period, ["child_support_expense"]),
        )
