from openfisca_us.model_api import *


class meets_snap_net_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP net income test"
    documentation = "Whether this SPM unit meets the SNAP net income test"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        income_limits = parameters(period).usda.snap.income_limits
        fpg = spm_unit("spm_unit_fpg", period)
        net_income_limit = income_limits.net.standard * fpg
        net_income = spm_unit("snap_net_income", period)
        return net_income <= net_income_limit
