from policyengine_us.model_api import *


class co_denver_property_tax_relief_renter_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "Eligible for the renter Denver Property Tax Relief"
    defined_for = "in_denver"
    definition_period = YEAR
    reference = "https://library.municode.com/co/denver/codes/code_of_ordinances?nodeId=TITIIREMUCO_CH53TAMIRE_ARTXIREPRTAASELLCOPROWTE_S53-492DE"  # 53-495 (e)

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.co.denver.dhs
        pays_rent = add(spm_unit, period, ["rent"]) > 0
        has_elderly_or_disabled = spm_unit(
            "has_co_denver_dhs_elderly_disabled", period
        )
        renters_with_elderly_or_disabled = has_elderly_or_disabled & pays_rent

        income = spm_unit("co_denver_property_tax_relief_income", period)
        size = spm_unit("spm_unit_size", period)
        ami = spm_unit.household("ami", period)
        p_hud = parameters(period).gov.hud.ami_limit
        size_limit = p_hud.family_size
        size_limit_excess = p_hud.per_person_exceeding_4
        size_exceeding_4 = max_(size - 4, 0)
        size_capped_at_4 = min_(size, 4)
        moderate = (
            size_limit.MODERATE[size_capped_at_4]
            + size_limit_excess.MODERATE * size_exceeding_4
        )
        ami_rate = p.property_tax_relief.ami_rate.renter.calc(size)
        renter_income_limit = ami * moderate * ami_rate

        renter_income_eligible = income <= renter_income_limit

        return renters_with_elderly_or_disabled & renter_income_eligible
