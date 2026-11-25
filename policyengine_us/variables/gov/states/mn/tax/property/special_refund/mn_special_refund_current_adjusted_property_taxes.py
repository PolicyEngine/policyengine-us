from policyengine_us.model_api import *


class mn_special_refund_current_adjusted_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund current taxes after home-use and improvement adjustments"
    unit = USD
    definition_period = YEAR
    defined_for = "mn_special_refund_inputs_available"
    reference = (
        # PDF pages 1-2
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=1",
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=12",
    )

    def formula_2025(tax_unit, period, parameters):
        current = tax_unit("mn_special_refund_current_property_taxes", period)
        current_use = tax_unit("mn_special_refund_current_home_use_fraction", period)
        prior_use = tax_unit("mn_special_refund_prior_home_use_fraction", period)
        line_1 = np.floor(current * min_(current_use, prior_use) + 0.5)
        improvements = tax_unit("mn_special_refund_improvement_value", period)
        market_value = tax_unit("mn_special_refund_taxable_market_value", period)
        improvement_share = np.divide(
            improvements,
            market_value,
            out=np.zeros_like(improvements),
            where=(improvements > 0) & (market_value > 0),
        )
        # Worksheet 3 rounds to a whole percentage before calculating excluded tax.
        improvement_share = np.floor(improvement_share * 100 + 0.5) / 100
        excluded_tax = np.floor(line_1 * improvement_share + 0.5)
        return line_1 - excluded_tax
