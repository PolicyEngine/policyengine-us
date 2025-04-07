from policyengine_us.model_api import *


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
            "state_supplement",
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
            # One-time energy relief payments.
            # Paid at the same time as the Alaska Permanent Fund Dividend,
            # which is part of IRS gross income.
            "ak_energy_relief",
            # Contributed.
            "basic_income",
            "ny_drive_clean_rebate",
        ]
        if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
            BENEFITS.append("aca_ptc")
        if not parameters(period).gov.hud.abolition:
            BENEFITS.append("spm_unit_capped_housing_subsidy")
        return add(spm_unit, period, BENEFITS)
