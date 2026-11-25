from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_eligible(Variable):
    """An active source-qualified election, independent of amount availability.

    An actual valid retirement-exclusion claim disqualifies this credit even
    when both raw elections are supplied. The computed retirement optimizer is
    downstream of this variable and is deliberately not a legal-fact input.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit active eligibility"
    definition_period = YEAR
    defined_for = "wi_veterans_property_tax_credit_eligibility_available"
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/d",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        claimant = tax_unit("wi_veterans_property_tax_credit_claimant_type", period)
        types = claimant.possible_values
        allowed = (
            (claimant == types.ELIGIBLE_VETERAN)
            | (claimant == types.UNREMARRIED_SURVIVOR)
            | (claimant == types.ELIGIBLE_SPOUSE_SEPARATE_RETURN)
        )
        verified = tax_unit("wi_veterans_property_tax_credit_wdva_verified", period)
        property_qualified = tax_unit(
            "wi_veterans_property_tax_credit_property_qualified", period
        )
        permitted = tax_unit("wi_veterans_property_tax_credit_claim_permitted", period)
        elected = tax_unit("wi_veterans_property_tax_credit_elected", period)
        incompatible = tax_unit(
            "wi_veterans_property_tax_credit_incompatible_credit_claimed", period
        )
        retirement = tax_unit(
            "wi_veterans_property_tax_credit_retirement_income_exclusion_claimed",
            period,
        )
        return (
            allowed
            & verified
            & property_qualified
            & permitted
            & elected
            & ~incompatible
            & ~retirement
        )
