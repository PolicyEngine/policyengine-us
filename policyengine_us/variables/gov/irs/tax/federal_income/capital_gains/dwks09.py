from policyengine_us.model_api import *


class dwks09(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 2 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        # SchD lines 15 and 16, respectively
        qdiv_plus_ltcg = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "qualified_dividend_income"],
        )
        net_cg = min_(qdiv_plus_ltcg, tax_unit("net_capital_gains", period))
        # dwks08 = min(dwks03, dwks04)
        # dwks09 = max(0., dwks07 - dwks08)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks09=... COMMENT
        other_cg = add(tax_unit, period, ["non_sch_d_capital_gains"])
        mod_cg = where(other_cg > 0, other_cg, max_(0, net_cg) + other_cg)
        return max_(
            0,
            mod_cg - min_(0, tax_unit("investment_income_form_4952", period)),
        )
