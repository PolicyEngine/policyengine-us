from policyengine_us.model_api import *


class hi_ccap_copay_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii CCAP co-payment rate"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=35"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.copay
        countable_income = spm_unit("hi_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        # The co-payment tier is a function of the family's gross income
        # as a share of the federal poverty guidelines (HAR 17-798.3-14(3);
        # Exhibit II sliding fee scale, dated January 2, 2020). The dollar
        # columns in Exhibit II are just FPG x band, so the percentage is
        # independent of family size.
        fpg_ratio = where(fpg > 0, countable_income / fpg, 0)
        return p.rate.calc(fpg_ratio)
