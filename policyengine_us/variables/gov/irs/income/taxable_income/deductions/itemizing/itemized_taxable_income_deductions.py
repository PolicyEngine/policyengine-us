from policyengine_us.model_api import *


class itemized_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized taxable income deductions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        total_deductions = tax_unit(
            "total_itemized_taxable_income_deductions", period
        )
        reduction = tax_unit(
            "itemized_taxable_income_deductions_reduction", period
        )
        return max_(0, total_deductions - reduction)
