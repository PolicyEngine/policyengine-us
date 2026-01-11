from policyengine_us.model_api import *


class az_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dbmefaapolicy.azdes.gov/index.html#page/FAA5/"
        "CA_Payment_Standard_(A1_2fA2).html#wwpID0E0WHB0FA"
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Arizona uses monthly 1992 FPG baseline for payment standard
        # az_tanf_fpg_baseline is YEAR, auto-converted to monthly when called from MONTH context
        monthly_fpg_baseline = spm_unit("az_tanf_fpg_baseline", period)

        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard

        # A1 (high) if shelter costs > 0; A2 (low) otherwise
        shelter_cost = spm_unit("housing_cost", period)
        has_shelter_costs = shelter_cost > 0

        high_threshold = p.high * monthly_fpg_baseline
        low_threshold = p.low * monthly_fpg_baseline

        return where(has_shelter_costs, high_threshold, low_threshold)
