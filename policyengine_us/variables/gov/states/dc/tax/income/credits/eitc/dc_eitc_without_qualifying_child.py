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
        # calculate US EITC amount before phase-out
        us_eligible = tax_unit("eitc_eligible", period)
        us_eitc = us_eligible * tax_unit("eitc_phased_in", period)
        # phase out us_eitc for income above DC phase-out start threshold
        earnings = tax_unit("tax_unit_earned_income", period)
        us_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, us_agi)
        dc = parameters(period).gov.states.dc.tax.income.credits
        excess = max_(0, greater_of - dc.eitc.without_children.phase_out.start)
        dc_phase_out_amount = excess * dc.eitc.without_children.phase_out.rate
        return max_(0, us_eitc - dc_phase_out_amount)
