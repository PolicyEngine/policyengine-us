from policyengine_us.model_api import *


class vt_2017_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 other subtractions from federal taxable income"
    unit = USD
    documentation = (
        "Vermont's 2017 subtractions from federal taxable income that "
        "PolicyEngine does not calculate, entered as a positive amount: the "
        "capital gains exclusion under the law then in effect and the "
        "depreciation adjustment for property whose federal bonus "
        "depreciation was added back in an earlier year."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        # Former 32 V.S.A. § 5811(21), as amended by 2015 Vt. Acts No. 57, § 64.
        "https://legislature.vermont.gov/Documents/2016/Docs/ACTS/ACT057/ACT057%20As%20Enacted.pdf#page=89",
    )
