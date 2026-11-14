from policyengine_us.model_api import *


class mn_special_refund_prior_adjusted_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund prior taxes after home-use and prior-refund adjustments"
    unit = USD
    definition_period = YEAR
    defined_for = "mn_special_refund_inputs_available"
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.03#stat.290A.03.13",
        # PDF pages 1-2
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=1",
    )

    def formula_2025(tax_unit, period, parameters):
        prior = tax_unit("mn_special_refund_prior_property_taxes", period)
        fallback = tax_unit("mn_special_refund_prior_property_taxes_fallback", period)
        prior = where(prior > 0, prior, fallback)
        current_use = tax_unit("mn_special_refund_current_home_use_fraction", period)
        prior_use = tax_unit("mn_special_refund_prior_home_use_fraction", period)
        line_5 = np.floor(prior * min_(current_use, prior_use) + 0.5)
        prior_refund = tax_unit("mn_special_refund_prior_refund", period)
        refund_share = where(current_use < prior_use, current_use, 1)
        line_6 = np.floor(prior_refund * refund_share + 0.5)
        # A negative line 7 is disqualifying; eligibility must see the actual result.
        return line_5 - line_6
