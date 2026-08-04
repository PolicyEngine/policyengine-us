from policyengine_us.model_api import *


class hi_ccap_copay_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii CCAP co-payment rate"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=29"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.copay
        countable_income = spm_unit("hi_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        # Co-payment percentage is a function of the family's gross income
        # as a share of the federal poverty guidelines (HAR
        # 17-798.2-14(b)(4); Exhibit II sliding fee scale). The dollar
        # columns in Exhibit II are just FPG x band, so the percentage is
        # independent of family size.
        fpg_ratio = where(fpg > 0, countable_income / fpg, 0)
        return p.rate.calc(fpg_ratio)
