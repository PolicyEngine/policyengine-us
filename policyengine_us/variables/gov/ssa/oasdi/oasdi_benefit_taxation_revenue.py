from policyengine_us.model_api import *


class oasdi_benefit_taxation_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI modeled benefit taxation liability"
    documentation = (
        "The OASDI share of income tax on Social Security benefits: "
        "tob_revenue_oasdi, the tax attributable to section 86 inclusion "
        "before the 1993 amendments. It leaves out the HI share "
        "(tob_revenue_medicare_hi). The share carries a sign: a unit whose tax "
        "falls when its benefits enter income contributes a negative amount, "
        "so sum units without a floor."
    )
    unit = USD
    reference = "https://www.ssa.gov/OP_Home/comp2/F098-021.html"
    adds = ["tob_revenue_oasdi"]
