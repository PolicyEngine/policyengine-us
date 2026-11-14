from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_coordination_available(Variable):
    """Whether this return's cross-credit restriction can be established.

    A verified own or counterpart claim proves prohibition even when other facts
    or taxes are unknown. Without that positive branch, known own legal status
    and a known absent counterpart claim establish coordination. Preserved
    alternative calculations when false are compatibility behavior, not a
    validated lawful election. Contradictory supplied family claims are unknown.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans credit election coordination is known"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        available = tax_unit(
            "wi_veterans_property_tax_credit_eligibility_available", period
        )
        disallowed = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credits_disallowed",
            period,
        )
        spouse = tax_unit("wi_veterans_property_tax_credit_spouse_claim_status", period)
        incompatible = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credit_claimed", period
        )
        consistent = ~((spouse == spouse.possible_values.VALID_CLAIM) & incompatible)
        no_spouse_claim = spouse == spouse.possible_values.NOT_CLAIMED
        return consistent & (disallowed | (available & no_spouse_claim))
