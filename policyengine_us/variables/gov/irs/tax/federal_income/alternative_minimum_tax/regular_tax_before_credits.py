from policyengine_us.model_api import *


class regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Regular tax before credits"
    documentation = "Regular tax on regular taxable income before credits"
    unit = USD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        dwks1 = tax_unit("taxable_income", period)

        capital_gains = parameters(period).gov.irs.capital_gains.brackets

        dwks16 = min_(capital_gains.thresholds["1"][filing_status], dwks1)
        dwks17 = min_(tax_unit("dwks14", period), dwks16)
        dwks20 = dwks16 - dwks17
        lowest_rate_tax = capital_gains.rates["1"] * dwks20
        # Break in worksheet lines
        dwks13 = tax_unit("dwks13", period)
        dwks21 = min_(dwks1, dwks13)
        dwks22 = dwks20
        dwks23 = max_(0, dwks21 - dwks22)
        dwks25 = min_(capital_gains.thresholds["2"][filing_status], dwks1)
        dwks19 = tax_unit("dwks19", period)
        dwks26 = min_(dwks19, dwks20)
        dwks27 = max_(0, dwks25 - dwks26)
        dwks28 = min_(dwks23, dwks27)
        dwks29 = capital_gains.rates["2"] * dwks28
        dwks30 = dwks22 + dwks28
        dwks31 = dwks21 - dwks30
        dwks32 = capital_gains.rates["3"] * dwks31
        # Break in worksheet lines
        dwks33 = min_(
            tax_unit("dwks09", period),
            add(tax_unit, period, ["unrecaptured_section_1250_gain"]),
        )
        dwks10 = tax_unit("dwks10", period)
        dwks34 = dwks10 + dwks19
        dwks36 = max_(0, dwks34 - dwks1)
        dwks37 = max_(0, dwks33 - dwks36)

        p = parameters(period).gov.irs.income

        dwks38 = p.amt.capital_gains.capital_gain_excess_tax_rate * dwks37
        # Break in worksheet lines
        dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        dwks40 = dwks1 - dwks39
        dwks41 = p.amt.brackets.rates[-1] * dwks40

        # Compute regular tax using bracket rates and thresholds
        reg_taxinc = max_(0, dwks19)
        bracket_tops = p.bracket.thresholds
        bracket_rates = p.bracket.rates
        reg_tax = 0
        bracket_bottom = 0
        for i in range(1, len(list(bracket_rates.__iter__())) + 1):
            b = str(i)
            bracket_top = bracket_tops[b][filing_status]
            reg_tax += bracket_rates[b] * amount_between(
                reg_taxinc, bracket_bottom, bracket_top
            )
            bracket_bottom = bracket_top

        # Return to worksheet lines
        dwks42 = reg_tax
        dwks43 = dwks29 + dwks32 + dwks38 + dwks41 + dwks42 + lowest_rate_tax
        dwks44 = tax_unit("income_tax_main_rates", period)
        dwks45 = min_(dwks43, dwks44)
        return where(tax_unit("has_qdiv_or_ltcg", period), dwks45, dwks44)
