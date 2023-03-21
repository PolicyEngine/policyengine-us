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
        # Start by matching the federal EITC.
        p = parameters(
            period
        ).gov.states.dc.tax.income.credits.eitc.without_children
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        matched_eitc = federal_eitc * p.match
        # Then phase out for income above the phase-out threshold.
        earnings = tax_unit("tax_unit_earned_income", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(earnings, federal_agi)
        excess = max_(greater_of - p.phase_out.start, 0)
        phase_out_amount = excess * p.phase_out.rate
        return max_(federal_eitc - phase_out_amount, 0)
