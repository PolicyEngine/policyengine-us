from policyengine_us.model_api import *


class dwks09(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 2 of 6)"
    unit = USD
    reference = "https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf"

    def formula(tax_unit, period, parameters):
        # Schedule D lines 15 and 16 contain capital gains, not qualified
        # dividends. Dividends enter separately in dwks10; including them
        # here double counts them when short-term gains are positive.
        long_term_gains = add(tax_unit, period, ["long_term_capital_gains"])
        net_cg = min_(long_term_gains, tax_unit("net_capital_gains", period))
        other_cg = add(tax_unit, period, ["non_sch_d_capital_gains"])
        mod_cg = where(other_cg > 0, other_cg, max_(0, net_cg) + other_cg)
        return max_(
            0,
            mod_cg - min_(0, tax_unit("investment_income_form_4952", period)),
        )
