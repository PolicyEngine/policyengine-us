from policyengine_us.model_api import *


class vt_2017_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 subtractions from federal taxable income"
    unit = USD
    documentation = (
        "Vermont's 2017 subtractions from federal taxable income: income from "
        "U.S. obligations, taxable state and local income tax refunds, and "
        "other subtractions such as the capital gains exclusion and "
        "depreciation adjustments for property placed in service earlier."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        # Former 32 V.S.A. § 5811(21), as amended by 2015 Vt. Acts No. 57, § 64.
        "https://legislature.vermont.gov/Documents/2016/Docs/ACTS/ACT057/ACT057%20As%20Enacted.pdf#page=89",
    )

    adds = ["us_govt_interest", "salt_refund_income", "vt_2017_other_subtractions"]
