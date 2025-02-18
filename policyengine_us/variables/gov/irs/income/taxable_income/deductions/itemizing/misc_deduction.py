from policyengine_us.model_api import *


class misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Miscellaneous deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # We currently only model unreimbursed business employee expenses as miscellaneous expenses
        expense = add(
            tax_unit, period, ["unreimbursed_business_employee_expenses"]
        )
        p = parameters(period).gov.irs.deductions.itemized.misc
        misc_floor = p.floor * tax_unit("positive_agi", period)
        return max_(0, expense - misc_floor)
