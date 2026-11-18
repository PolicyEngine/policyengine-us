from policyengine_us.model_api import *


class mn_special_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special property tax refund"
    unit = USD
    definition_period = YEAR
    defined_for = "mn_special_refund_eligible"
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.04#stat.290A.04.2h",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=1",
    )

    def formula_2025(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.special_refund
        current = tax_unit("mn_special_refund_current_adjusted_property_taxes", period)
        prior = tax_unit("mn_special_refund_prior_adjusted_property_taxes", period)
        threshold = max_(
            np.floor(prior * p.increase_threshold + 0.5), p.minimum_increase
        )
        excess = max_(current - prior - threshold, 0)
        return min_(np.floor(excess * p.refund_rate + 0.5), p.maximum_refund)
