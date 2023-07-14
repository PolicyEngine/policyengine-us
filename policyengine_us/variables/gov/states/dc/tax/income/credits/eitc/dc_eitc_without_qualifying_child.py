from policyengine_us.model_api import *


class dc_eitc_without_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC without qualifying children"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = "eitc_eligible"

    def formula(tax_unit, period, parameters):
        # calculate DC EITC amount before phase out
        earnings = tax_unit("tax_unit_earned_income", period)
        p = parameters(period).gov.states.dc.tax.income.credits
        uncapped_eitc = earnings * p.eitc.without_children.phase_in.rate
        capped_eitc = min_(p.eitc.without_children.phase_in.max, uncapped_eitc)
        # phase out capped_eitc for income above DC phase-out start threshold
        us_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, us_agi)
        excess = max_(0, greater_of - p.eitc.without_children.phase_out.start)
        phase_out_amount = excess * p.eitc.without_children.phase_out.rate
        return max_(0, capped_eitc - phase_out_amount)
