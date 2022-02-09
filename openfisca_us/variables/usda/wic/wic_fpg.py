from openfisca_us.model_api import *


class wic_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Federal poverty guideline for WIC, with family size incremented by one for pregnant women"
    label = "Pregnancy-adjusted poverty line for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_D"
    unit = USD

    def formula(spm_unit, period, parameters):
        pregnant = spm_unit.any(spm_unit.members("is_pregnant", period))
        normal_fpg = spm_unit("spm_unit_fpg", period)
        state_group = spm_unit.household("state_group_str", period)
        additional = parameters(period).hhs.fpg.additional_person[state_group]
        return normal_fpg + additional * pregnant
