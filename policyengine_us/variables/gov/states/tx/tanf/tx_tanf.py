from policyengine_us.model_api import *


class tx_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2410-general-policy",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Compare monthly TANF benefit with monthly equivalent of OTTANF
        # Return whichever is higher for the household

        # Regular TANF: monthly benefit
        regular_tanf = spm_unit("tx_regular_tanf", period)

        # OTTANF: one-time payment divided by 12 for monthly equivalent
        ottanf = spm_unit("tx_ottanf", period)

        return max_(regular_tanf, ottanf)
