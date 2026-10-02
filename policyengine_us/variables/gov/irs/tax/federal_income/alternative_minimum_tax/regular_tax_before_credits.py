from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    tax_at_main_rates,
)
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)


class regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Regular tax before credits"
    documentation = "Regular tax on regular taxable income before credits"
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        # A Form 2555 filer enters line 3 of the Foreign Earned Income Tax
        # Worksheet on line 1 and refigures the capital gain lines for any
        # capital gain excess (26 U.S.C. 911(f)).
        dwks1 = tax_unit("taxable_income_plus_section_911_exclusion", period)
        worksheet = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, tax_unit("section_911_capital_gain_excess", period)
        )

        dwks16 = min_(p.capital_gains.thresholds["1"][filing_status], dwks1)
        dwks17 = min_(tax_unit("dwks14", period), dwks16)
        dwks20 = dwks16 - dwks17
        lowest_rate_tax = p.capital_gains.rates["1"] * dwks20
        # Break in worksheet lines
        dwks13 = worksheet.line_13
        dwks21 = min_(dwks1, dwks13)
        dwks22 = dwks20
        dwks23 = max_(0, dwks21 - dwks22)
        dwks25 = min_(p.capital_gains.thresholds["2"][filing_status], dwks1)
        dwks19 = tax_unit("dwks19", period)
        dwks26 = min_(dwks19, dwks20)
        dwks27 = max_(0, dwks25 - dwks26)
        dwks28 = min_(dwks23, dwks27)
        dwks29 = p.capital_gains.rates["2"] * dwks28
        dwks30 = dwks22 + dwks28
        dwks31 = dwks21 - dwks30
        dwks32 = p.capital_gains.rates["3"] * dwks31
        # Break in worksheet lines
        dwks33 = min_(worksheet.line_9, worksheet.unrecaptured_section_1250_gain)
        dwks10 = worksheet.line_10
        dwks34 = dwks10 + dwks19
        dwks36 = max_(0, dwks34 - dwks1)
        dwks37 = max_(0, dwks33 - dwks36)

        dwks38 = p.income.amt.capital_gains.capital_gain_excess_tax_rate * dwks37
        # Break in worksheet lines
        dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        dwks40 = dwks1 - dwks39
        dwks41 = p.income.amt.brackets.rates[-1] * dwks40

        # Compute regular tax using bracket rates and thresholds
        # The shared schedule clamps inverted brackets as in
        # income_tax_main_rates (#9084), or the AMT comparator diverges from
        # the main-rates tax and manufactures phantom AMT for qdiv/LTCG
        # filers.
        reg_taxinc = max_(0, dwks19)
        reg_tax = tax_at_main_rates(reg_taxinc, filing_status, p.income.bracket)

        # Return to worksheet lines
        dwks42 = reg_tax
        dwks43 = dwks29 + dwks32 + dwks38 + dwks41 + dwks42 + lowest_rate_tax
        # Foreign Earned Income Tax Worksheet, lines 4 to 6: the worksheet
        # tax on line 3 less the tax on the excluded amount alone.
        # income_tax_main_rates is already net of it.
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        tax_on_excluded = tax_at_main_rates(excluded, filing_status, p.income.bracket)
        dwks43 = where(excluded > 0, max_(0, dwks43 - tax_on_excluded), dwks43)
        dwks44 = tax_unit("income_tax_main_rates", period)
        dwks45 = min_(dwks43, dwks44)
        return where(tax_unit("has_qdiv_or_ltcg", period), dwks45, dwks44)
