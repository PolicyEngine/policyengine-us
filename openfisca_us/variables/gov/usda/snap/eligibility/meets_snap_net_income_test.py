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
        net_income_limit_fpg = parameters(
            period
        ).gov.usda.snap.income.limit.net
        net_income_fpg = spm_unit("snap_net_income_fpg_ratio", period)
        return net_income_fpg <= net_income_limit_fpg
