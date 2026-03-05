from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ct_hb5009() -> Reform:
    class ct_property_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Connecticut property tax credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.cga.ct.gov/2026/TOB/H/PDF/2026HB-05009-R00-HB.PDF"
        )
        defined_for = "ct_property_tax_credit_eligible"

        def formula(tax_unit, period, parameters):
            agi = tax_unit("ct_agi", period)
            filing_status = tax_unit("filing_status", period)

            # Use HB-5009 parameters
            p = parameters(period).gov.contrib.states.ct.hb5009

            # Get property taxes paid
            real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])

            # Calculate credit with increased cap
            max_credit = min_(real_estate_taxes, p.cap)

            # Phase-out calculation using HB-5009 parameters
            start = p.phaseout.start[filing_status]
            limit = p.phaseout.limit[filing_status]
            increment = p.phaseout.increment[filing_status]
            rate = p.phaseout.rate

            # Calculate stepped reduction
            excess = max_(agi - start, 0)
            total_increments = np.ceil(excess / increment)
            reduction_percent = rate * total_increments
            reduction_amount = max_credit * reduction_percent

            # Apply minimum floor between start and limit
            # Above limit: no credit at all
            credit_after_reduction = max_credit - reduction_amount
            minimum_floor = p.minimum
            below_limit = agi <= limit
            credit_with_floor = max_(credit_after_reduction, minimum_floor)
            # Cap at actual property taxes paid
            credit_capped = min_(credit_with_floor, max_credit)
            credit = where(
                max_credit > 0,
                where(below_limit, credit_capped, 0),
                0,
            )

            return credit

    class reform(Reform):
        def apply(self):
            self.update_variable(ct_property_tax_credit)

    return reform


def create_ct_hb5009_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ct_hb5009()

    p = parameters.gov.contrib.states.ct.hb5009

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ct_hb5009()
    else:
        return None


ct_hb5009 = create_ct_hb5009_reform(None, None, bypass=True)
