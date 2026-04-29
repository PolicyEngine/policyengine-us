from policyengine_us.model_api import *


class me_ccap_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine CCAP monthly parent fee"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = (
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=26",
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=27",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ccap.copay
        countable_income = spm_unit("me_ccap_countable_income", period)
        monthly_smi = spm_unit("me_ccap_smi", period)
        smi_percentage = where(monthly_smi > 0, countable_income / monthly_smi, 0)
        weekly_income = countable_income * MONTHS_IN_YEAR / WEEKS_IN_YEAR

        fee_rate = p.rate.calc(smi_percentage)
        raw_weekly_fee = np.floor(weekly_income * fee_rate)

        cap_rate = p.cap.calc(smi_percentage)
        capped_weekly_fee = np.floor(weekly_income * cap_rate)

        weekly_fee = min_(raw_weekly_fee, capped_weekly_fee)
        return weekly_fee * WEEKS_IN_YEAR / MONTHS_IN_YEAR
