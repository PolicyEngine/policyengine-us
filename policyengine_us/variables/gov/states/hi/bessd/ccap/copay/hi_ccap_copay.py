from policyengine_us.model_api import *


class hi_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Hawaii CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = (
        "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=35",
        "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=29",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.copay
        copay_rate = spm_unit("hi_ccap_copay_rate", period)
        # From August 6, 2021, the co-payment is the sliding-fee tier
        # multiplied by the family unit's monthly gross income, assessed
        # once per family (HAR 17-798.3-14). Before then, it was the
        # tier multiplied by the department's maximum rate allowable,
        # per child in care (HAR 17-798.2-14(b)(4)).
        countable_income = spm_unit("hi_ccap_countable_income", period)
        maximum_monthly_rate = add(spm_unit, period, ["hi_ccap_maximum_monthly_rate"])
        base = where(p.income_based_in_effect, countable_income, maximum_monthly_rate)
        return base * copay_rate
