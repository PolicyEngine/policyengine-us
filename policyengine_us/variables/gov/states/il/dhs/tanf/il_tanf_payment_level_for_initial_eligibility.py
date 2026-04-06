from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.tanf.il_tanf_county_group import (
    ILTANFCountyGroup,
)


class il_tanf_payment_level_for_initial_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) payment level for initial eligibility"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.payment_level
        unit_size = spm_unit("il_tanf_assistance_unit_size", period)

        if p.regional_in_effect:
            county_group = spm_unit("il_tanf_county_group", period)
            is_group_i = county_group == ILTANFCountyGroup.GROUP_I
            is_group_iii = county_group == ILTANFCountyGroup.GROUP_III
            return select(
                [is_group_i, is_group_iii],
                [
                    p.regional.group_i.amount.calc(unit_size),
                    p.regional.group_iii.amount.calc(unit_size),
                ],
                default=p.regional.group_ii.amount.calc(unit_size),
            )

        fpg = spm_unit("il_tanf_assistance_unit_fpg", period)
        return p.rate * fpg
