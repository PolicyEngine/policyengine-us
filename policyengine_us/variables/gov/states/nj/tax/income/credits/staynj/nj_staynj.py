from policyengine_us.model_api import *


class nj_staynj(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Stay NJ Property Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.HTM",
        "https://www.nj.gov/treasury/taxation/staynj/index.shtml",
    )
    defined_for = "nj_staynj_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.staynj

        # Get property taxes paid
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])

        # Per P.L. 2024 c.88: Stay NJ = max(min(property_taxes * rate, max_benefit) - ANCHOR - Senior Freeze, 0)
        target_benefit = min_(property_taxes * p.rate, p.max_benefit)

        # Subtract ANCHOR and Senior Freeze benefits
        anchor_benefit = tax_unit("nj_anchor", period)
        senior_freeze = tax_unit("nj_senior_freeze", period)

        return max_(target_benefit - anchor_benefit - senior_freeze, 0)
