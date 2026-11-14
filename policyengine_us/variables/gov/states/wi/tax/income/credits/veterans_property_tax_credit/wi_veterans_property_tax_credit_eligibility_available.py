from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_eligibility_available(Variable):
    """Legal facts are known, apart from the independently recorded monetary total.

    A counterpart valid veterans claim and actual incompatible family claim
    contradict one another. That record produces unavailable framework defaults
    for all six derived outputs, without choosing which filed claim prevails.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit legal eligibility is known"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        facts = tax_unit("wi_veterans_property_tax_credit_facts_available", period)
        claimant = tax_unit("wi_veterans_property_tax_credit_claimant_type", period)
        spouse = tax_unit("wi_veterans_property_tax_credit_spouse_claim_status", period)
        incompatible = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credit_claimed", period
        )
        consistent = ~((spouse == spouse.possible_values.VALID_CLAIM) & incompatible)
        return facts & (claimant != claimant.possible_values.UNKNOWN) & consistent
