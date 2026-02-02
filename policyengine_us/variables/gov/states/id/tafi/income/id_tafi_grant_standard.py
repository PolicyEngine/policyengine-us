from policyengine_us.model_api import *


class id_tafi_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho TAFI grant standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.249",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.250",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252",
    )
    defined_for = StateCode.ID

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi
        countable_earned = spm_unit("id_tafi_countable_earned_income", period)
        countable_unearned = spm_unit(
            "id_tafi_countable_unearned_income", period
        )
        work_incentive = spm_unit("id_tafi_work_incentive_amount", period)

        # With earned: work_incentive - earned; Without: maximum_grant
        base = where(
            countable_earned > 0,
            work_incentive - countable_earned,
            p.maximum_grant,
        )
        return max_(base - countable_unearned, 0)
