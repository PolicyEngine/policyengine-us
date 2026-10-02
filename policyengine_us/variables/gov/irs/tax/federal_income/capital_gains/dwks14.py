from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 5 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        # Line 1 is taxable income, or for a Form 2555 filer line 3 of the
        # Foreign Earned Income Tax Worksheet, and line 13 reflects any
        # capital gain excess.
        dwks01 = tax_unit("taxable_income_plus_section_911_exclusion", period)
        excess = tax_unit("section_911_capital_gain_excess", period)
        dwks13 = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, excess
        ).line_13
        return max_(0, dwks01 - dwks13) * tax_unit("has_qdiv_or_ltcg", period)
