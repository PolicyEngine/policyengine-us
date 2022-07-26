from openfisca_us.model_api import *


class in_taxes_after_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN taxes after credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        county_tax_before_credits = tax_unit("in_county_tax", period)
        local_non_refundable_credits = tax_unit(
            "in_local_non_refundable_credits", period
        )
        county_tax_after_non_refundable_credits = _max(
            0, county_tax_before_credits - local_non_refundable_credits
        )
        state_tax_before_credits = tax_unit("in_state_agi_tax", period)
        state_non_refundable_credits = tax_unit(
            "in_state_non_refundable_credits", period
        )
        state_tax_after_non_refundable_credits = _max(
            0, state_tax_before_credits - state_non_refundable_credits
        )
        tax_after_non_refundable_credits = (
            county_tax_after_non_refundable_credits
            + state_tax_after_non_refundable_credits
        )
        return tax_after_non_refundable_credits - tax_unit(
            "in_refundable_credits", period
        )
        # This will go negative. Need feedback on whether should instead floor this at zero and add a refund variable.
