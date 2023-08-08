from policyengine_us.model_api import *


class household_state_income_tax(Variable):
    # This definition contains all modelled states, and exists to solve circular dependencies in state_income_tax.
    value_type = float
    entity = TaxUnit
    label = "household State tax"
    unit = USD
    definition_period = YEAR
    adds = [
        "ca_income_tax_before_refundable_credits",
        "dc_income_tax_before_refundable_credits",
        "ia_income_tax_before_refundable_credits",
        "il_total_tax",
        "ks_income_tax_before_refundable_credits",
        "me_income_tax_before_refundable_credits",
        "ma_income_tax_before_refundable_credits",
        "md_income_tax_before_refundable_credits",
        "mn_income_tax_before_refundable_credits",
        "mo_income_tax_before_refundable_credits",
        "nd_income_tax_before_refundable_credits",
        "ne_income_tax_before_refundable_credits",
        "nh_income_tax_before_refundable_credits",
        "nj_income_tax_before_refundable_credits",
        "ny_income_tax_before_refundable_credits",
        "or_income_tax_before_refundable_credits",
        "pa_income_tax",
        "wa_income_tax_before_refundable_credits",
        "nyc_income_tax_before_refundable_credits",
        "ut_income_tax_before_refundable_credits",
        "wi_income_tax_before_refundable_credits",
    ]
    subtracts = [
        "ca_refundable_credits",  # California.
        "dc_refundable_credits",  # District of Columbia.
        "ia_refundable_credits",  # Iowa.
        "il_refundable_credits",  # Illinois.
        "ks_refundable_credits",  # Kansas.
        "ma_refundable_credits",  # Massachusetts.
        "me_refundable_credits",  # Maine.
        "md_refundable_credits",  # Maryland.
        "mn_refundable_credits",  # Minnesota.
        "mo_refundable_credits",  # Missouri.
        "nd_refundable_credits",  # North Dakota.
        "ne_refundable_credits",  # Nebraska.
        "nh_refundable_credits",  # New Hampshire.
        "ny_refundable_credits",  # New York.
        "or_refundable_credits",  # Oregon.
        # Skip PA, which has no refundable credits.
        "wa_refundable_credits",  # Washington.
        "nyc_refundable_credits",  # New York City.
        "ut_refundable_credits",  # Utah.
        "wi_refundable_credits",  # Wisconsin.
    ]
