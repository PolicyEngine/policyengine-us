from policyengine_us.model_api import *


class az_ccap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona Child Care Assistance Program income limit"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap.income
        family_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(family_size, 1, p.max_family_size)
        enrolled = spm_unit("az_ccap_enrolled", period)
        return where(
            enrolled,
            p.threshold.level_7[capped_size],
            p.threshold.level_6[capped_size],
        )
