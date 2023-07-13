from policyengine_us.model_api import *


class dc_eitc_without_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC without qualifying children"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # apply DC match rate to federal EITC
        us_eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.dc.tax.income.credits
        matched_eitc = us_eitc * p.eitc.without_children.match
        # phase out matched_eitc for income above DC phase-out threshold
        earnings = tax_unit("tax_unit_earned_income", period)
        us_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, us_agi)
        excess = max_(greater_of - p.eitc.without_children.phase_out.start, 0)
        phase_out_amount = excess * p.eitc.without_children.phase_out.rate
        return max_(matched_eitc - phase_out_amount, 0)
