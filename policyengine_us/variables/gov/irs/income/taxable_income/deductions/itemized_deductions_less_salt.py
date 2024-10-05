from policyengine_us.model_api import *


class itemized_deductions_less_salt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized tax deductions other than SALT deduction"
    unit = USD
    documentation = "Non-SALT itemized deductions total."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        return add(tax_unit, period, deductions)
