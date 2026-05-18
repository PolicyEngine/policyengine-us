from policyengine_us.model_api import *


class fl_tca_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.FL
    documentation = """
    Returns the high-shelter tier maximum benefit amount, following CBPP
    and WRD conventions for cross-state comparison. This is the payment
    standard for households with monthly shelter costs exceeding $50.

    For actual benefit calculation based on household shelter status, use
    fl_tca_payment_standard instead.
    """

    def formula(spm_unit, period, parameters):
        # CBPP/WRD convention: report the high-shelter tier
        p = parameters(period).gov.states.fl.dcf.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_family_size)
        return p.payment_standard.high_shelter[capped_size]
