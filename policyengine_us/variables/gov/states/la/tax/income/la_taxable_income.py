from policyengine_us.model_api import *


class la_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana taxable income"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("la_agi", period)

        itemizes = tax_unit("tax_unit_itemizes", period)
        # Louisana does not provide a standard deduction
        itemized_deductions = tax_unit("la_itemized_deductions", period)
        claimed_itemized_deductions = itemizes * itemized_deductions
        fed_tax_deduction = tax_unit("la_federal_tax_deduction", period)
        p = parameters(period).gov.states.la.tax.income.deductions.standard
        if p.applies:
            standard_deduction = tax_unit("la_standard_deductions", period)
            return max_(
                agi
                - standard_deduction
                - claimed_itemized_deductions
                - fed_tax_deduction,
                0,
            )
        return max_(
            agi - claimed_itemized_deductions - fed_tax_deduction,
            0,
        )
