from policyengine_us.model_api import *


class itemized_taxable_income_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized taxable income deductions reduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.reduction
        if p.applies:
            agi = tax_unit("adjusted_gross_income", period)

            filing_status = tax_unit("filing_status", period)
            agi_threshold = p.agi_threshold[filing_status]
            agi_excess = max_(0, agi - agi_threshold)
            agi_excess_reduction = agi_excess * p.rate.excess_agi
            maximum_deductions = tax_unit(
                "total_itemized_taxable_income_deductions", period
            )
            maximum_deductions_reduction = maximum_deductions * p.rate.base
            return min_(agi_excess_reduction, maximum_deductions_reduction)
        return 0
