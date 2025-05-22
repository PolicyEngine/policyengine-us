from policyengine_us.model_api import *


class wic_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Federal poverty guideline for WIC, with family size incremented by one for pregnant women"
    label = "Pregnancy-adjusted poverty line for WIC"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_D"
    unit = USD

    def formula(spm_unit, period, parameters):
        pregnant = spm_unit.any(spm_unit.members("is_pregnant", period))
        # The system divides annual variables by 12 automatically when bringing them down to a month.
        # The normal FPG is an annual variable, so the system divides it by 12 by default.
        normal_fpg = spm_unit("spm_unit_fpg", period)
        state_group = spm_unit.household("state_group_str", period)
        additional = parameters(period).gov.hhs.fpg.additional_person[
            state_group
        ]
        annual_pregnant_addition = additional * pregnant
        # The additional amount is based on a yearly parameter, so we need to manually divide it by 12.
        monthly_pregnant_addition = annual_pregnant_addition / MONTHS_IN_YEAR
        return normal_fpg + monthly_pregnant_addition
