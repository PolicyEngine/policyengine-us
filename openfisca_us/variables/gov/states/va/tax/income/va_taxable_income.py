from openfisca_us.model_api import *

class va_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        va_deductions_path = (
            gov.states.va.tax.deductions.standard_deduction
        )
        itemized = tax_unit("va_itemized_deductions")
        standard = va_deductions_path[tax_unit("filing_status", period)]
        adj_deductions = tax_unit("va_adj_deductions")
        total_deductions = max(itemized, standard) + adj_deductions

        return tax_unit("va_adjusted_gross_income", period) - total_deductions