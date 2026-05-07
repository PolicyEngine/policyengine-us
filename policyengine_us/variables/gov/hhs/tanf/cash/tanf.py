from policyengine_us.model_api import *

# All implemented state TANF programs.
# Most use {st}_tanf naming; some states have their own program names.
STATE_TANF_VARIABLES = [
    # Standard {st}_tanf naming (28 states)
    "al_tanf",
    "az_tanf",
    "ca_tanf",
    "co_tanf",
    "dc_tanf",
    "de_tanf",
    "ga_tanf",
    "hi_tanf",
    "il_tanf",
    "in_tanf",
    "ks_tanf",
    "me_tanf",
    "mo_tanf",
    "ms_tanf",
    "mt_tanf",
    "nc_tanf",
    "nd_tanf",
    "nv_tanf",
    "ny_tanf",
    "ok_tanf",
    "or_tanf",
    "pa_tanf",
    "sc_tanf",
    "sd_tanf",
    "tx_tanf",
    "va_tanf",
    "wa_tanf",
    # Non-standard program names (23 states + DC)
    "ak_atap",  # Alaska Temporary Assistance Program
    "ar_tea",  # Arkansas Transitional Employment Assistance
    "ct_tfa",  # Connecticut Temporary Family Assistance
    "fl_tca",  # Florida Temporary Cash Assistance
    "ia_fip",  # Iowa Family Investment Program
    "id_tafi",  # Idaho Temporary Assistance for Families
    "ky_ktap",  # Kentucky K-TAP
    "la_fitap",  # Louisiana Family Independence TAP
    "ma_tafdc",  # Massachusetts TAFDC
    "md_tca",  # Maryland Temporary Cash Assistance
    "mi_fip",  # Michigan Family Independence Program
    "mn_mfip",  # Minnesota Family Investment Program
    "ne_adc",  # Nebraska Aid to Dependent Children
    "nh_fanf",  # New Hampshire FANF
    "nj_wfnj",  # New Jersey WorkFirst New Jersey
    "nm_works",  # New Mexico Works
    "oh_owf",  # Ohio Works First
    "ri_works",  # Rhode Island Works
    "tn_ff",  # Tennessee Families First
    "ut_fep",  # Utah Family Employment Program
    "vt_reach_up",  # Vermont Reach Up
    "wi_works",  # Wisconsin Works (W-2)
    "wv_works",  # West Virginia Works
    "wy_power",  # Wyoming POWER
]


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received, "
        "summing all state-specific TANF programs."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.tanf
        if p.abolish_tanf:
            return 0

        takes_up = spm_unit("takes_up_tanf_if_eligible", period)
        value = add(spm_unit, period, STATE_TANF_VARIABLES)
        return value * takes_up
