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
        # Manual §4080-4 B catastrophic medical (>10% income) is not modeled — PolicyEngine
        # does not track catastrophic medical as a category separate from routine OOP medical.
        # Manual §4080-4 C educational income/expense pair: educational income is not in
        # our unearned_sources whitelist, so omitting the matching deduction is internally
        # consistent (net zero effect on countable income).
        earned = spm_unit("ak_ccap_countable_earned_income", period)
        unearned = spm_unit("ak_ccap_countable_unearned_income", period)
        child_support = add(spm_unit, period, ["child_support_expense"])
        return max_(0, earned + unearned - child_support)
