from policyengine_us.model_api import *


class wv_property_tax_credits_applied(Variable):
    """Apply the two property tax credits with a shared tax-liability pool."""

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "West Virginia property tax credits applied against income tax"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/",
        "https://code.wvlegislature.gov/11-21-23/",
    )
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        available = tax_unit("wv_property_tax_credits_applied_available", period)
        senior_credit = tax_unit("wv_sctc", period)
        homestead_credit = tax_unit("wv_homestead_excess_property_tax_credit", period)
        liability = max_(tax_unit("wv_income_tax_before_refundable_credits", period), 0)
        p = parameters(period).gov.states.wv.tax.income.credits
        senior_restricted = senior_credit < p.sctc.refund_minimum
        homestead_restricted = homestead_credit < p.heptc.refund_minimum
        restricted = where(senior_restricted, senior_credit, 0) + where(
            homestead_restricted, homestead_credit, 0
        )
        refundable = where(senior_restricted, 0, senior_credit) + where(
            homestead_restricted, 0, homestead_credit
        )
        # Inference: maximize lawful use by allocating liability to credits that
        # cannot be refunded. The statutes do not expressly order this allocation.
        applied = refundable + min_(restricted, liability)
        return where(available, applied, 0)
