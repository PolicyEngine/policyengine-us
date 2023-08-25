from policyengine_us.model_api import *


class misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Miscellaneous deduction"
    unit = USD
    definition_period = YEAR

    reference = "https://www.irs.gov/publications/p529, Introduction Line #3"

    def formula(tax_unit, period, parameters):
        # calculate federal level miscellaneous cap
        p = parameters(period).gov.irs.deductions.itemized.misc
        misc_floor = p.floor * tax_unit("positive_agi", period)
        cap = max_(0, misc_floor)

        # individial miscellaneous income
        misc_income = add(tax_unit, period, ["miscellaneous_income"])
        return min_(misc_income, cap)
