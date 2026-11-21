from policyengine_us.model_api import *


class ct_temporary_premium_assistance_fpl_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Temporary Premium Assistance income as a share of the federal poverty line"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://www.accesshealthct.com/financial-help/",
        "https://www.accesshealthct.com/federal-changes-to-health-coverage/",
        "https://help.accesshealthct.com/en_US/premium-assistance",
    )
    documentation = (
        "Household income (ACA MAGI) as a share of the federal poverty line "
        "for the premium tax credit tax family (aca_fpg, the prior-year "
        "guideline), the basis of the federal credit that Temporary Premium "
        "Assistance tops up. Access Health CT states its bands in dollars "
        "of that guideline, from the guideline itself to twice it and from "
        "one cent above four times it to five times it, so the bands are "
        "decided on this exact ratio, not the truncated aca_magi_fraction. "
        "Negative income counts as zero. A household with no poverty "
        "guideline gets an infinite ratio, as in aca_magi_fraction, which "
        "fails every band."
    )

    def formula(tax_unit, period, parameters):
        magi = max_(tax_unit("aca_magi", period), 0).astype(np.float64)
        guideline = tax_unit("aca_fpg", period)
        # aca_fpg is 0 where HHS defines no guideline. Divide by 1 there to
        # avoid dividing by zero, then return an infinite ratio, which is
        # above every band, as aca_magi_fraction does.
        has_guideline = guideline > 0
        # Divide in float64: a float32 quotient can round a ratio just above
        # a band edge down onto it. The result is stored as float32, but for
        # a whole-dollar guideline the smallest float32 income above 1, 2, 4
        # or 5 times the guideline still rounds to a stored ratio above it.
        ratio = magi / where(has_guideline, guideline, 1)
        return where(has_guideline, ratio, np.inf)
