from policyengine_us.model_api import *


class wv_property_tax_credits_applied_available(Variable):
    """Bounded credit coordination and valid amounts, not complete return data."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia property tax credit application can be determined"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/",
        "https://code.wvlegislature.gov/11-21-23/",
    )
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        coordinated = tax_unit("wv_heptc_coordination_available", period)
        senior_credit = tax_unit("wv_sctc", period)
        homestead_credit = tax_unit("wv_homestead_excess_property_tax_credit", period)
        tax_before_credits = tax_unit("wv_income_tax_before_refundable_credits", period)
        liability = max_(tax_before_credits, 0)
        return (
            coordinated
            & np.isfinite(senior_credit)
            & np.isfinite(homestead_credit)
            & np.isfinite(tax_before_credits)
            & (senior_credit >= 0)
            & (homestead_credit >= 0)
            & (liability >= 0)
        )
