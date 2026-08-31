from policyengine_us.model_api import *


class hi_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Hawaii CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=35"

    def formula(spm_unit, period, parameters):
        # Co-payment = (co-payment tier from the sliding fee scale) x
        # (monthly gross income for the family unit) (HAR 17-798.3-14(4)).
        countable_income = spm_unit("hi_ccap_countable_income", period)
        copay_rate = spm_unit("hi_ccap_copay_rate", period)
        return countable_income * copay_rate
