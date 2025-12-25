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
        p = parameters(period).gov.states.id.tanf
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        countable_earned = spm_unit("id_tafi_countable_earned_income", period)
        countable_unearned = spm_unit(
            "id_tafi_countable_unearned_income", period
        )
        work_incentive = spm_unit("id_tafi_work_incentive_amount", period)

        has_earned_income = gross_earned > 0
        has_only_unearned = ~has_earned_income & (countable_unearned > 0)

        # Per IDAPA 16.03.08.252: Families with earned income use work incentive table
        earned_income_grant = (
            work_incentive - countable_earned - countable_unearned
        )

        # Per IDAPA 16.03.08.250: Families with unearned only use maximum grant
        unearned_only_grant = p.maximum_grant - countable_unearned

        # Per IDAPA 16.03.08.249: Families with no income get maximum grant
        return select(
            [has_earned_income, has_only_unearned],
            [earned_income_grant, unearned_only_grant],
            default=p.maximum_grant,
        )
