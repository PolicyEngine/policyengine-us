from policyengine_us.model_api import *


class meets_snap_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP net income test"
    documentation = "Whether this SPM unit meets the SNAP net income test"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.income.limit
        net_income = spm_unit("snap_net_income", period)
        fpg = spm_unit("snap_fpg", period)
        # 7 CFR 273.9(a)(3): the monthly standard is the poverty guideline
        # divided by 12, rounded up to the next whole dollar.
        # Pre-round to 4 decimals so float error on an exact whole-dollar
        # standard cannot push the ceiling up an extra dollar.
        limit = np.ceil(np.round(p.net * fpg, 4))
        return net_income <= limit
