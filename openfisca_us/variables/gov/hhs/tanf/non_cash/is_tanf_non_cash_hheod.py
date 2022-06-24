from openfisca_us.model_api import *


class is_tanf_non_cash_hheod(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Elderly or disabled for TANF non-cash benefit"
    documentation = "Whether the household is considered elderly or disabled for TANF non-cash benefit for SNAP BBCE"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        bbce = parameters(period).gov.hhs.tanf.non_cash
        requires_all = bbce.requires_all_for_hheod[state]
        return where(
            requires_all,
            spm_unit("has_all_usda_elderly_disabled", period),
            spm_unit("has_usda_elderly_disabled", period),
        )
