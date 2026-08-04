from policyengine_us.model_api import *


class hi_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Hawaii CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=29"

    def formula(spm_unit, period, parameters):
        # Co-payment = (department's maximum rate allowable) x (co-payment
        # percentage from the sliding fee scale) (HAR 17-798.2-14(b)(4)).
        # The percentage multiplies the provider max rate, not gross income.
        maximum_monthly_rate = add(spm_unit, period, ["hi_ccap_maximum_monthly_rate"])
        copay_rate = spm_unit("hi_ccap_copay_rate", period)
        return maximum_monthly_rate * copay_rate
