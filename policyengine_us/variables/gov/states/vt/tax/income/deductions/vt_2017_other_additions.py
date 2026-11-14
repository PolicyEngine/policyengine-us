from policyengine_us.model_api import *


class vt_2017_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 additions to federal taxable income"
    unit = USD
    documentation = (
        "Vermont's 2017 additions to federal taxable income other than the "
        "itemized deduction addback: interest on non-Vermont state and local "
        "obligations and the adjustment for federal bonus depreciation under "
        "26 U.S.C. § 168(k). As in Vermont's AGI additions, all tax-exempt "
        "interest is added; vt_other_additions carries the rest."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        # Former 32 V.S.A. § 5811(21), as amended by 2015 Vt. Acts No. 57, § 64.
        "https://legislature.vermont.gov/Documents/2016/Docs/ACTS/ACT057/ACT057%20As%20Enacted.pdf#page=89",
    )

    adds = ["tax_exempt_interest_income", "vt_other_additions"]
