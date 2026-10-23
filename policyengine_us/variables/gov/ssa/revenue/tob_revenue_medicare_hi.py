from policyengine_us.model_api import *


class tob_revenue_medicare_hi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue credited to Medicare HI under section 121(e)(1)(B), as "
        "amended by OBRA 1993 section 13215(c). HI receives the increase in "
        "tax liability attributable to the 1993 amendments: total taxation-of-"
        "benefits revenue less the pre-1993 OASDI allocation. Both amounts "
        "use branches to calculate signed marginal income tax liabilities, "
        "retaining negative unit differences for aggregation."
    )
    unit = USD
    reference = "https://www.ssa.gov/OP_Home/comp2/F098-021.html"

    def formula(tax_unit, period, parameters):
        total = tax_unit("tob_revenue_total", period)
        oasdi = tax_unit("tob_revenue_oasdi", period)
        return total - oasdi
