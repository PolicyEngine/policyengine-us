from policyengine_us.model_api import *


def create_baby_bonus_act() -> Reform:
    class baby_bonus(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "Baby Bonus Act payment"
        unit = USD
        documentation = (
            "One-time payment for newborns under the Baby Bonus Act"
        )
        reference = "placeholder - bill not yet introduced"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.baby_bonus_act

            age = person("age", period)
            max_age = p.max_child_age
            is_eligible_child = age < max_age

            amount = p.amount

            return is_eligible_child * amount

    class household_benefits(Variable):
        value_type = float
        entity = Household
        label = "benefits"
        unit = USD
        definition_period = YEAR
        adds = [
            "social_security",
            "ssi",
            "snap",
            "wic",
            "free_school_meals",
            "reduced_price_school_meals",
            "spm_unit_broadband_subsidy",
            "tanf",
            "high_efficiency_electric_home_rebate",
            "residential_efficiency_electrification_rebate",
            "unemployment_compensation",
            # Contributed.
            "basic_income",
            "spm_unit_capped_housing_subsidy",
            "household_state_benefits",
            "baby_bonus",
        ]

    class spm_unit_benefits(Variable):
        value_type = float
        entity = SPMUnit
        label = "Benefits"
        definition_period = YEAR
        unit = USD

        def formula(spm_unit, period, parameters):
            BENEFITS = [
                "social_security",
                "ssi",
                "ma_state_supplement",  # Massachusetts benefits
                # California programs.
                "ca_cvrp",  # California Clean Vehicle Rebate Project.
                # Colorado programs.
                "co_ccap_subsidy",
                "co_state_supplement",
                "co_oap",
                "snap",
                "wic",
                "free_school_meals",
                "reduced_price_school_meals",
                "spm_unit_broadband_subsidy",
                "spm_unit_energy_subsidy",
                "tanf",
                "high_efficiency_electric_home_rebate",
                "residential_efficiency_electrification_rebate",
                "unemployment_compensation",
                # Contributed.
                "basic_income",
                "ny_drive_clean_rebate",
                "baby_bonus",
            ]
            if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
                BENEFITS.append("aca_ptc")
            if not parameters(period).gov.hud.abolition:
                BENEFITS.append("spm_unit_capped_housing_subsidy")
            return add(spm_unit, period, BENEFITS)

    class reform(Reform):
        def apply(self):
            self.update_variable(baby_bonus)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)

    return reform


def create_baby_bonus_act_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_baby_bonus_act()

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.income_security_package.baby_bonus_act

    if p.in_effect:
        return create_baby_bonus_act()
    else:
        return None


baby_bonus_act = create_baby_bonus_act_reform(None, None, bypass=True)
