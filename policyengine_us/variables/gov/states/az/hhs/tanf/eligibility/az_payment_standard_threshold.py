from policyengine_us.model_api import *


class az_payment_standard_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment Standard"
    definition_period = MONTH
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        monthly_fpg_baseline = spm_unit("az_fpg_baseline", period)
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        high_threshold = p.high * monthly_fpg_baseline
        low_threshold = p.low * monthly_fpg_baseline
        shelter_cost = spm_unit("housing_cost", period)

        return where(shelter_cost > 0, high_threshold, low_threshold)
