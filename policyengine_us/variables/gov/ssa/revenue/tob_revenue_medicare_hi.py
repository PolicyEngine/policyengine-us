from policyengine_us.model_api import *


class tob_revenue_medicare_hi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue credited to Medicare HI under section 121(e)(1)(B), as "
        "amended by OBRA 1993 section 13215(c). HI receives the increase in "
        "chapter 1 income tax liability after nonrefundable credits and "
        "before refundable credits attributable to the 1993 amendments: "
        "total taxation-of-"
        "benefits revenue less the pre-1993 OASDI allocation. Both amounts "
        "exclude chapter 2A net investment income tax under section 1411 and "
        "use branches to calculate signed marginal chapter 1 liabilities, "
        "retaining negative unit differences for aggregation. The OASDI "
        "allocation caps old-law inclusion at actual inclusion, so HI gets "
        "nothing from a unit whose inclusion does not exceed the pre-1993 "
        "amount."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/401",
        "https://www.law.cornell.edu/uscode/text/26/1411",
        "https://www.ssa.gov/OP_Home/comp2/F098-021.html",
    )

    def formula(tax_unit, period, parameters):
        total = tax_unit("tob_revenue_total", period)
        oasdi = tax_unit("tob_revenue_oasdi", period)
        return total - oasdi
