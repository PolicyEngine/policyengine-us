from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.snap.income.snap_income_standard_helpers import (
    snap_monthly_income_standard,
)


class meets_snap_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP net income test"
    documentation = "Whether this SPM unit meets the SNAP net income test"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
        "https://www.law.cornell.edu/cfr/text/7/273.9#a_3_ii",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.income.limit
        net_income = spm_unit("snap_net_income", period)
        # 7 CFR 273.9(a)(3)(ii): the monthly standard is the poverty
        # guideline divided by 12, rounded up to the next whole dollar, with
        # a separately rounded per-person increment for large households.
        limit = snap_monthly_income_standard(spm_unit, period, parameters, p.net)
        return net_income <= limit
