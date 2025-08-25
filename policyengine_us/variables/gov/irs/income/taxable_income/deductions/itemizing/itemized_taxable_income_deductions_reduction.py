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
            if p.amended_structure.applies:
                top_rate_threshold = parameters(
                    period
                ).gov.irs.income.bracket.thresholds["6"][filing_status]
                exemptions = tax_unit("exemptions", period)
                taxable_income = max_(0, agi - exemptions)
                taxable_income_excess = max_(
                    0, taxable_income - top_rate_threshold
                )
                total_itemized_deductions = tax_unit(
                    "total_itemized_taxable_income_deductions", period
                )
                lesser_of_deductions_or_excess = min_(
                    total_itemized_deductions, taxable_income_excess
                )
                return (
                    p.amended_structure.rate * lesser_of_deductions_or_excess
                )
            return min_(agi_excess_reduction, maximum_deductions_reduction)
        return 0
