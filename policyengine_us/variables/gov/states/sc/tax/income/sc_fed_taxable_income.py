from policyengine_us.model_api import *


class sc_fed_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina federal taxable income exculde salt"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        deductions = tax_unit("itemized_deductions_less_salt", period)
        return max_(0, agi - deductions)
