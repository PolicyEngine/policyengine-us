from policyengine_us.model_api import *


class mn_special_refund_inputs_available(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota special refund required tax history is available"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2",
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=12",
    )

    def formula_2025(tax_unit, period, parameters):
        current = tax_unit("mn_special_refund_current_property_taxes", period)
        prior = tax_unit("mn_special_refund_prior_property_taxes", period)
        fallback = tax_unit("mn_special_refund_prior_property_taxes_fallback", period)
        prior_refund = tax_unit("mn_special_refund_prior_refund", period)
        improvements = tax_unit("mn_special_refund_improvement_value", period)
        market_value = tax_unit("mn_special_refund_taxable_market_value", period)
        current_use = tax_unit("mn_special_refund_current_home_use_fraction", period)
        prior_use = tax_unit("mn_special_refund_prior_home_use_fraction", period)
        veteran_exclusion = tax_unit(
            "mn_special_refund_disabled_veteran_exclusion", period
        )
        prior_available = (prior > 0) | (
            (prior == 0) & ((fallback > 0) | ((fallback == 0) & veteran_exclusion))
        )
        improvements_available = (improvements == 0) | (
            (improvements > 0) & (market_value > 0)
        )
        return (
            (current >= 0)
            & prior_available
            & (prior_refund >= 0)
            & improvements_available
            & (current_use >= 0)
            & (current_use <= 1)
            & (prior_use >= 0)
            & (prior_use <= 1)
        )
