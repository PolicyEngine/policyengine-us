from policyengine_us.model_api import *


class is_tanf_non_cash_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligibility for TANF non-cash benefit"
    documentation = "Eligibility for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        gross = spm_unit("meets_tanf_non_cash_gross_income_test", period)
        net = spm_unit("meets_tanf_non_cash_net_income_test", period)
        asset = spm_unit("meets_tanf_non_cash_asset_test", period)
        return gross & net & asset
