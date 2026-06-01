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
            "in_ssp",
            "ct_ssp",
            "ga_ssp",
            "al_ssp",
            "ak_ssp",
            "dc_ossp",  # DC benefits
            "id_aabd",  # Idaho benefits
            "ky_ssp",  # Kentucky benefits
            "de_ssp",  # Delaware benefits
            "fl_oss",
            "ks_sspp",  # Kansas benefits
            "hi_oss",
            "la_oss",  # Louisiana benefits
            "ma_state_supplement",  # Massachusetts benefits
            "md_paa",  # Maryland benefits
            "wa_ssp",  # Washington benefits
            "mi_ssp",  # Michigan benefits
            "me_ssp",  # Maine benefits
            "mo_ssp",  # Missouri benefits
            "mn_msa",  # Minnesota benefits
            # California programs.
            "ca_cvrp",  # California Clean Vehicle Rebate Project.
            # Colorado programs.
            "co_ccap_subsidy",
            "co_state_supplement",
            "co_oap",
            # Washington programs.
            "wa_child_care_subsidies",
            # New Mexico programs.
            "nm_ssi_state_supplement",
            # South Carolina programs.
            "sc_ssi_state_supplement",
            # Texas programs.
            "tx_ssi_state_supplement",
            # West Virginia programs.
            "wv_child_care_subsidies",
            "snap",
            "wic",
            "free_school_meals",
            "reduced_price_school_meals",
            "child_support_received",
            "workers_compensation",
            "educational_assistance",
            "financial_assistance",
            "survivor_benefits",
            "spm_unit_energy_subsidy",
            "tanf",
            # Washington (WA) cash-assistance programs. wa_sfa and wa_rca
            # sit alongside the federal TANF aggregator entry; under default
            # rules these three are mutually exclusive at the SPM-unit level
            # so summing them does not double-count.
            "wa_sfa",
            "wa_rca",
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
            BENEFITS.append("assigned_aca_ptc")
        if not parameters(period).gov.hud.abolition:
            BENEFITS.append("spm_unit_capped_housing_subsidy")
        return add(spm_unit, period, BENEFITS)
