from policyengine_us.model_api import *


class az_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.azleg.gov/ars/46/00207-01.htm",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.AZ
    documentation = """
    Returns the with-shelter tier (A1) maximum benefit amount, following CBPP
    and WRD conventions for cross-state comparison. This is the base payment
    standard before the 37% reduction for households without shelter costs.

    For actual benefit calculation based on household shelter status, use
    az_tanf_payment_standard instead.
    """

    def formula(spm_unit, period, parameters):
        # CBPP/WRD convention: report the with-shelter (A1) tier
        # This is the base payment standard without the reduction
        monthly_fpg_baseline = spm_unit("az_tanf_fpg_baseline", period)
        p = parameters(period).gov.states.az.hhs.tanf.payment_standard
        return p.rate * monthly_fpg_baseline
