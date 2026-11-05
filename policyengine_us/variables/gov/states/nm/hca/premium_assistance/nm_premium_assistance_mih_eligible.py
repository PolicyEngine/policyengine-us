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
    # This reuses the Marketplace enrollment test (pays_aca_premium) and the
    # married-filing-separately exclusion from federal ACA PTC eligibility, but
    # not its FPL-band income test, which fails above 400% FPL.
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/50c9a4d0-d5c8-48aa-8b9a-5c43e8fa23bc/Addendum%201_MAP%20P&P%20Middle%20Income%20Household.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        in_effect = p.mih.in_effect
        # Reuse the enrollment internals of is_aca_ptc_eligible: on-Marketplace
        # enrollment (pays_aca_premium) and the married-filing-separately
        # exclusion. Since policyengine-us #9506 pays_aca_premium also excludes
        # the Medicaid coverage gap, income under the federal PTC floor of 100%
        # FPL; that cannot bind here, because income_eligible already requires
        # income above 400% FPL.
        pays_premium = add(tax_unit, period, ["pays_aca_premium"]) > 0
        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        # is_aca_ptc_eligible does not embed the federal PTC filing requirement
        # (IRC 36B(a); aca_ptc does), so gate it explicitly here. Unlike the
        # base component, this one serves income above the federal PTC limit,
        # where no federal credit exists to take up, so ACA take-up cannot
        # stand for filing (files_return_for_aca_ptc); only filing for another
        # reason counts.
        is_filer = tax_unit("tax_unit_is_filer", period)
        # Addendum 1, Section I.A(3): "Have a household income above 400% of
        # the FPL." Test the exact ratio, not the truncated aca_magi_fraction:
        # truncation maps 400.00%-400.99% to 4.00, which would leave incomes
        # just above 400% out of both this component and the base program.
        magi = max_(tax_unit("aca_magi", period), 0)
        exact_magi_frac = magi / tax_unit("tax_unit_fpg", period.last_year)
        income_eligible = exact_magi_frac > p.fpl_limit
        return in_effect & pays_premium & not_separate & is_filer & income_eligible
