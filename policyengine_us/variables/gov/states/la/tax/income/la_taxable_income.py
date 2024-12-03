from policyengine_us.model_api import *


class la_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana taxable income"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        itemized_deductions = tax_unit("la_itemized_deductions", period)
        claimed_itemized_deductions = itemizes * itemized_deductions
        fed_tax_deduction = tax_unit("la_federal_tax_deduction", period)
        agi = tax_unit("la_agi", period)
        total_deductions = claimed_itemized_deductions + fed_tax_deduction
        p = parameters(period).gov.states.la.tax.income.deductions.standard
        if p.applies:
            standard_deduction = tax_unit("la_standard_deduction", period)
            total_deductions += standard_deduction

        return max_(agi - total_deductions, 0)
