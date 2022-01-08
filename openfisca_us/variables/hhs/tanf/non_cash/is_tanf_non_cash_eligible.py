from openfisca_us.model_api import *


class is_tanf_non_cash_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligibility for TANF non-cash benefit"
    documentation = "Eligibility for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("meets_tanf_non_cash_income_test", period)
        asset_eligible = spm_unit("meets_tanf_non_cash_asset_test", period)
        return income_eligible & asset_eligible
