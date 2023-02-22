from policyengine_us.model_api import *


class dc_eitc_without_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC Without Qualifying Child Amount"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        employment_income = tax_unit("employment_income", period)
        p = parameters(period).gov.states.dc.tax.income.credits.eitc.no_children.phase_out
        tent_eitc = tax_unit("earned_income_tax_credit", period)
        fed_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(employment_income, fed_agi)
        phase_out_amount = max_(greater_of - p.start, 0) * p.rate
        dc_eitc = max_(tent_eitc - phase_out_amount, 0)

        return dc_eitc