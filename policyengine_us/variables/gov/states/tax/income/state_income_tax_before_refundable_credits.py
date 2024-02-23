from policyengine_us.model_api import *


class state_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = [
        "al_income_tax_before_refundable_credits",
        "az_income_tax_before_refundable_credits",
        "co_income_tax_before_refundable_credits",
        "dc_income_tax_before_refundable_credits",
        "de_income_tax_before_refundable_credits",
        "ga_income_tax_before_refundable_credits",
        "hi_income_tax_before_refundable_credits",
        "ia_income_tax_before_refundable_credits",
        "il_total_tax",
        "in_income_tax_before_refundable_credits",
        "ks_income_tax_before_refundable_credits",
        "ma_income_tax_before_refundable_credits",
        "md_income_tax_before_refundable_credits",
        "me_income_tax_before_refundable_credits",
        "mn_income_tax_before_refundable_credits",
        "mo_income_tax_before_refundable_credits",
        "nc_income_tax",  # NC has no refundable credits.
        "nd_income_tax_before_refundable_credits",
        "ne_income_tax_before_refundable_credits",
        "nh_income_tax_before_refundable_credits",
        "nj_income_tax_before_refundable_credits",
        "nm_income_tax_before_refundable_credits",
        "ny_income_tax_before_refundable_credits",
        "or_income_tax_before_refundable_credits",
        "pa_income_tax",  # PA has no refundable credits.
        "ri_income_tax_before_refundable_credits",
        "sc_income_tax_before_refundable_credits",
        "vt_income_tax_before_refundable_credits",
        "wa_income_tax_before_refundable_credits",
        "wi_income_tax_before_refundable_credits",
    ]
