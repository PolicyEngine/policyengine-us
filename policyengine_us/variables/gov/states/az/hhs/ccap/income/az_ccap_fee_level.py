from policyengine_us.model_api import *


class az_ccap_fee_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Arizona Child Care Assistance Program fee level"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.income
        family_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(family_size, 1, p.max_family_size)
        income = spm_unit("az_ccap_countable_income", period)
        return select(
            [
                income <= p.threshold.level_1[capped_size],
                income <= p.threshold.level_2[capped_size],
                income <= p.threshold.level_3[capped_size],
                income <= p.threshold.level_4[capped_size],
                income <= p.threshold.level_5[capped_size],
                income <= p.threshold.level_6[capped_size],
                income <= p.threshold.level_7[capped_size],
            ],
            [1, 2, 3, 4, 5, 6, 7],
            default=0,
        )
