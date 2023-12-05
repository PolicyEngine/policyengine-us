from policyengine_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax"
    unit = USD
    definition_period = YEAR
    adds = [
        # state income tax variables listed in alphabetical order:
        # "ak_income_tax",  --- no state income tax
        "al_income_tax",
        "ar_income_tax",
        "az_income_tax",
        # "ca_income_tax",  --- activating will cause circular logic errors
        # "co_income_tax",  --- activating will cause circular logic errors
        "ct_income_tax",
        # "dc_income_tax",  --- activating will cause circular logic errors
        "de_income_tax",
        # "fl_income_tax",  --- no state income tax
        # "ga_income_tax",  --- activating will cause circular logic errors
        "hi_income_tax",
        # "ia_income_tax",  --- activating will cause circular logic errors
        "id_income_tax",
        "il_income_tax",
        "in_income_tax",
        "ks_income_tax",
        "ky_income_tax",
        "la_income_tax",
        # "ma_income_tax",  --- activating will cause circular logic errors
        # "md_income_tax",  --- activating will cause circular logic errors
        # "me_income_tax",  --- activating will cause circular logic errors
        "mi_income_tax",
        "mn_income_tax",
        # "mo_income_tax",  --- activating will cause circular logic errors
        "ms_income_tax",
        "mt_income_tax",
        "nc_income_tax",
        # "nd_income_tax",  --- activating will cause circular logic errors
        # "ne_income_tax",  --- activating will cause circular logic errors
        "nh_income_tax",
        "nj_income_tax",
        # "nm_income_tax",  --- activating will cause circular logic errors
        # "nv_income_tax",  --- no state income tax
        # "ny_income_tax",  --- activating will cause circular logic errors
        # "oh_income_tax",  --- activating will cause circular logic errors
        # "ok_income_tax",  --- activating will cause circular logic errors
        # "or_income_tax",  --- activating will cause circular logic errors
        "pa_income_tax",
        "ri_income_tax",
        # "sc_income_tax",  --- activating will cause circular logic errors
        # "sd_income_tax",  --- no state income tax
        # "tn_income_tax",  --- no state income tax
        # "tx_income_tax",  --- no state income tax
        # "ut_income_tax",  --- activating will cause circular logic errors
        "va_income_tax",
        # "vt_income_tax",  --- activating will cause circular logic errors
        "wa_income_tax",
        "wi_income_tax",
        "wv_income_tax",
        # "wy_income_tax",  --- no state income tax
    ]

    def formula(tax_unit, period, parameters):
        if parameters(period).simulation.reported_state_income_tax:
            spm_unit = tax_unit.spm_unit
            person = spm_unit.members
            is_head = person("is_tax_unit_head", period)
            total_tax_unit_heads = spm_unit.sum(is_head)
            spm_unit_state_tax = spm_unit(
                "spm_unit_state_tax_reported", period
            )
            return where(
                total_tax_unit_heads > 0,
                spm_unit_state_tax / total_tax_unit_heads,
                0,
            )
        else:
            return add(tax_unit, period, state_income_tax.adds)
