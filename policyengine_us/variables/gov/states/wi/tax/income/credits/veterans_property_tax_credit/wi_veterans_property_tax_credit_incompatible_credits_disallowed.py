from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_incompatible_credits_disallowed(Variable):
    """A verified own or counterpart-spouse election prohibits alternatives.

    This restriction does not depend on known or positive taxes, the reformable
    rate or the refund amount. False with unavailable coordination is not
    verified permission to combine credits. Contradictory supplied family claims
    return the framework false default without adjudicating either filed claim.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans claim prohibits incompatible credits"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        eligible = tax_unit("wi_veterans_property_tax_credit_eligible", period)
        spouse = tax_unit("wi_veterans_property_tax_credit_spouse_claim_status", period)
        incompatible = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credit_claimed", period
        )
        spouse_claims = spouse == spouse.possible_values.VALID_CLAIM
        consistent = ~(spouse_claims & incompatible)
        return consistent & (eligible | spouse_claims)
