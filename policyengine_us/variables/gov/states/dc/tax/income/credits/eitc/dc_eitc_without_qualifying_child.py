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
        # 0.0765 * max(employment_income, 7650)
        p = parameters(period).gov.states.dc.tax.income.credits.eitc.not_qualifying
        tent_eitc =  p.percent * min_(employment_income, p.cap)
        fed_agi = tax_unit("adjusted_gross_income", period)
        greater_of = max_(employment_income, fed_agi)
        tent_eitc_2 = max_(tent_eitc - ((greater_of - p.agi_floor) * p.agi_multiplier), 0)

        return where(fed_agi > p.agi_ceiling, 0,
            where(fed_agi > p.agi_floor, tent_eitc_2, tent_eitc)
        )