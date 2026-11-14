from policyengine_us.model_api import *


class mn_special_refund_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Minnesota special property tax refund"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.04#stat.290A.04.2h",
        "https://www.revisor.mn.gov/statutes/cite/290A.03#stat.290A.03.8",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=1",
    )

    def formula_2025(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.property.special_refund
        available = tax_unit("mn_special_refund_inputs_available", period)
        same_homestead = tax_unit("mn_special_refund_same_homestead", period)
        qualifying_claimant = tax_unit("mn_special_refund_qualifying_claimant", period)
        claimants = tax_unit.members("is_tax_unit_head_or_spouse", period)
        claimant_is_dependent = tax_unit.any(
            claimants & tax_unit.members("is_tax_unit_dependent", period)
        )
        dependent_elsewhere = tax_unit(
            "head_is_dependent_elsewhere", period
        ) | tax_unit("spouse_is_dependent_elsewhere", period)
        current = tax_unit("mn_special_refund_current_adjusted_property_taxes", period)
        prior = tax_unit("mn_special_refund_prior_adjusted_property_taxes", period)
        increase = current - prior
        threshold = max_(
            np.floor(prior * p.increase_threshold + 0.5), p.minimum_increase
        )
        return (
            available
            & same_homestead
            & qualifying_claimant
            & ~claimant_is_dependent
            & ~dependent_elsewhere
            & (prior >= 0)
            & (prior <= current)
            & (increase >= p.minimum_increase)
            & (increase > threshold)
        )
