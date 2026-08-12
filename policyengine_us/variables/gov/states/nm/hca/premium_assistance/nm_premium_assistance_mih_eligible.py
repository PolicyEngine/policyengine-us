from policyengine_us.model_api import *


class nm_premium_assistance_mih_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for New Mexico Premium Assistance Middle Income Household component"
    )
    definition_period = YEAR
    defined_for = StateCode.NM
    # A tax unit is eligible for the Middle Income Household component when that
    # component is in effect, at least one member is enrolled on the
    # Marketplace, the tax unit files a federal return and does not file
    # separately, and household income is above the federal poverty line limit.
    # This reuses the non-income pieces of federal ACA PTC eligibility
    # (Marketplace enrollment and the married-filing-separately exclusion) but
    # not the income test, which fails above 400% FPL.
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/50c9a4d0-d5c8-48aa-8b9a-5c43e8fa23bc/Addendum%201_MAP%20P&P%20Middle%20Income%20Household.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        in_effect = p.mih.in_effect
        # Reuse the non-income internals of is_aca_ptc_eligible: on-Marketplace
        # enrollment and the married-filing-separately exclusion.
        pays_premium = add(tax_unit, period, ["pays_aca_premium"]) > 0
        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        # is_aca_ptc_eligible does not embed the federal PTC filing requirement
        # (IRC 36B(a); aca_ptc does), so gate it explicitly here.
        is_filer = tax_unit("tax_unit_is_filer", period)
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_frac > p.fpl_limit
        return in_effect & pays_premium & not_separate & is_filer & income_eligible
