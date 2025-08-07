from policyengine_us.model_api import *


class co_denver_property_tax_relief_homeowner_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "Eligible for the homeowner Denver Property Tax Relief"
    defined_for = "in_denver"
    definition_period = YEAR
    reference = "https://library.municode.com/co/denver/codes/code_of_ordinances?nodeId=TITIIREMUCO_CH53TAMIRE_ARTXIREPRTAASELLCOPROWTE_S53-492DE"  # 53-495 (d)

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.co.denver.dhs
        pays_property_taxes = add(spm_unit, period, ["real_estate_taxes"]) > 0
        has_elderly_or_disabled = spm_unit(
            "has_co_denver_dhs_elderly_disabled", period
        )
        count_dependents = add(spm_unit, period, ["tax_unit_dependents"])
        has_dependents = count_dependents > 0
        homeowners_with_elderly_or_disabled_or_dependents = (
            has_elderly_or_disabled | has_dependents
        ) & pays_property_taxes

        income = spm_unit("co_denver_property_tax_relief_income", period)
        ami = spm_unit.household("ami", period)
        moderate_factor = spm_unit("hud_moderate_income_factor", period)
        homeowner_income_limit = (
            ami * moderate_factor * p.property_tax_relief.ami_rate.homeowner
        )

        homeowner_income_eligible = income <= homeowner_income_limit

        return (
            homeowners_with_elderly_or_disabled_or_dependents
            & homeowner_income_eligible
        )
