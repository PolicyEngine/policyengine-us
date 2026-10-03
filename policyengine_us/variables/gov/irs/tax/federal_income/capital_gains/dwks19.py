from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 6 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.capital_gains
        dwks14 = tax_unit("dwks14", period)
        filing_status = tax_unit("filing_status", period)
        # Line 1 is taxable income, or for a Form 2555 filer line 3 of the
        # Foreign Earned Income Tax Worksheet, and line 10 reflects any
        # capital gain excess.
        dwks01 = tax_unit("taxable_income_plus_section_911_exclusion", period)
        dwks16 = min_(p.thresholds["1"][filing_status], dwks01)
        dwks17 = min_(dwks14, dwks16)
        dwks10 = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, tax_unit("taxable_income", period)
        ).line_10
        dwks18 = max_(0, dwks01 - dwks10)
        return max_(dwks17, dwks18) * tax_unit("has_qdiv_or_ltcg", period)
