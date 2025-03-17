from policyengine_us.model_api import *


class misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Miscellaneous deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/67#b"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.misc
        if p.applies:
            expenses = tax_unit("total_misc_deductions", period)
            misc_floor = p.floor * tax_unit("positive_agi", period)
            return max_(0, expenses - misc_floor)
        return 0
