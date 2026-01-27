from policyengine_us.model_api import *


class ak_atap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.485",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Per 7 AAC 45.480: Work incentive deduction applies per person
        # Per 7 AAC 45.485: Childcare deduction applies at household level
        person_countable = add(
            spm_unit, period, ["ak_atap_countable_earned_income_person"]
        )
        childcare_deduction = spm_unit("ak_atap_childcare_deduction", period)
        return max_(person_countable - childcare_deduction, 0)
