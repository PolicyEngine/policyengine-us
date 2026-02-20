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

        # Get ANCHOR benefit received (must be subtracted per NJ Treasury)
        anchor_benefit = tax_unit("nj_anchor", period)

        # Calculate 50% of (property taxes minus ANCHOR)
        # Per NJ Treasury: Stay NJ benefit is 50% of property taxes
        # MINUS any payments received through ANCHOR
        net_property_taxes = max_(property_taxes - anchor_benefit, 0)
        calculated_benefit = net_property_taxes * p.rate

        # Cap at maximum benefit
        return min_(calculated_benefit, p.max_benefit)
