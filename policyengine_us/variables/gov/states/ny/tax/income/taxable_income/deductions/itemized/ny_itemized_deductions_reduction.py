from policyengine_us.model_api import *


class ny_itemized_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY itemized deductions reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized
        agi = tax_unit("ny_agi", period)
        itemized_deduction = tax_unit("ny_itemized_deductions_max", period)
        #if agi <= 475_000; single: 100_000, joint: 20_000, hoh: 250_000
        #    return 0
        #if 475_000 < agi <= 525_000;
        #    return 25% * itemized_deduction
        #else: 
        #    return 50% * itemized_deduction
        return p.amount.calc(agi) * itemized_deduction
        # if 1_000_000 < agi <= 10_000_000, 
            return 50% * charitaele_contributions
        # if 10_000_000 < agi, 
            return 25% * charitaele_contributions