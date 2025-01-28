from policyengine_us.model_api import *


class adjusted_capital_gains_reduced_by_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRS Form 1040 Schedule D worksheet (part 2 of 6)"  # DWKS09
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2023.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        # SchD lines 15 and 16, respectively
        qdiv_plus_ltcg = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "qualified_dividend_income"],
        )  # p23250
        # Schedule D Tax Worksheet line 7
        capped_net_capital_gains = min_(
            qdiv_plus_ltcg, tax_unit("net_capital_gains", period)
        )  # dwks7
        # Schedule D Tax Worksheet line 8
        # dwks8 = min(dwks3, dwks4)
        # Schedule D Tax Worksheet line 9
        # adjusted_capital_gains_reduced_by_investment_income = max(0., capped_net_capital_gains - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF adjusted_capital_gains_reduced_by_investment_income=... COMMENT
        other_cg = add(tax_unit, period, ["non_sch_d_capital_gains"])  # e01100
        mod_cg = where(
            other_cg > 0,
            other_cg,
            max_(0, capped_net_capital_gains) + other_cg,
        )  # c24510
        return max_(
            0,
            mod_cg - min_(0, tax_unit("investment_income_form_4952", period)),
        )
