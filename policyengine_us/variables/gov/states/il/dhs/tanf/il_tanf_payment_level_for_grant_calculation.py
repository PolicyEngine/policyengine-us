from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.tanf.il_tanf_county_group import (
    ILTANFCountyGroup,
)


class il_tanf_payment_level_for_grant_calculation(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) payment level for grant calculation"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.payment_level
        parent_count = add(spm_unit, period, ["il_tanf_payment_eligible_parent"])
        child_count = add(spm_unit, period, ["il_tanf_payment_eligible_child"])
        child_only = (child_count > 0) & (parent_count == 0)
        unit_size = spm_unit("il_tanf_assistance_unit_size", period)

        if p.regional_in_effect:
            county_group = spm_unit("il_tanf_county_group", period)
            is_group_i = county_group == ILTANFCountyGroup.GROUP_I
            is_group_iii = county_group == ILTANFCountyGroup.GROUP_III
            with_adult = select(
                [is_group_i, is_group_iii],
                [
                    p.regional.group_i.amount.calc(unit_size),
                    p.regional.group_iii.amount.calc(unit_size),
                ],
                default=p.regional.group_ii.amount.calc(unit_size),
            )
            child_only_amount = select(
                [is_group_i, is_group_iii],
                [
                    p.regional.group_i.child_only_amount.calc(unit_size),
                    p.regional.group_iii.child_only_amount.calc(unit_size),
                ],
                default=p.regional.group_ii.child_only_amount.calc(unit_size),
            )
            return where(child_only, child_only_amount, with_adult)

        # Post-2018: FPG-percentage system per § 112.251
        fpg = spm_unit("il_tanf_assistance_unit_fpg", period)
        parent_only = (parent_count > 0) & (child_count == 0)
        parent_and_child_present = (parent_count > 0) & (child_count > 0)
        base_payment = p.rate * fpg
        parent_only_payment = p.parent_only_rate * base_payment
        child_only_payment = p.child_only_rate * base_payment

        return select(
            [parent_only, child_only, parent_and_child_present],
            [
                parent_only_payment,
                child_only_payment,
                base_payment,
            ],
            default=0,
        )
