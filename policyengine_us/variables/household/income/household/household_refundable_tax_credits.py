from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD
    adds = [
        "income_tax_refundable_credits",  # Federal.
        "al_refundable_credits",  # Alabama.
        "az_refundable_credits",  # Arizona.
        "ca_refundable_credits",  # California.
        "co_refundable_credits",  # Colorado.
        "dc_refundable_credits",  # District of Columbia.
        "de_refundable_credits",  # Delaware.
        "ga_refundable_credits",  # Georgia.
        "ia_refundable_credits",  # Iowa.
        "il_refundable_credits",  # Illinois.
        "in_refundable_credits",  # Indiana.
        "ks_refundable_credits",  # Kansas.
        "ma_refundable_credits",  # Massachusetts.
        "me_refundable_credits",  # Maine.
        "md_refundable_credits",  # Maryland.
        "mn_refundable_credits",  # Minnesota.
        "mo_refundable_credits",  # Missouri.
        # Skip NC, which has no refundable credits.
        "nd_refundable_credits",  # North Dakota.
        "ne_refundable_credits",  # Nebraska.
        "nh_refundable_credits",  # New Hampshire.
        "nj_refundable_credits",  # New Jersey.
        "nm_refundable_credits",  # New Mexico.
        "ny_refundable_credits",  # New York.
        "ok_refundable_credits",  # Oklahoma.
        "or_refundable_credits",  # Oregon.
        # Skip PA, which has no refundable credits.
        "ri_refundable_credits",  # Rhode Island.
        "sc_refundable_credits",  # South Carolina.
        "wa_refundable_credits",  # Washington.
        "ut_refundable_credits",  # Utah.
        "vt_refundable_credits",  # Vermont.
        "wi_refundable_credits",  # Wisconsin.
        # LOCAL
        "nyc_refundable_credits",  # New York City.
    ]

    def formula(household, period, parameters):
        added_components = household_refundable_tax_credits.adds
        params = parameters(period)
        p = params.gov.contrib.ubi_center.flat_tax
        if p.abolish_federal_income_tax:
            added_components = [
                c
                for c in added_components
                if c != "income_tax_refundable_credits"
            ]
        if params.simulation.reported_state_income_tax:
            added_components = [
                "income_tax_refundable_credits",  # Federal.
            ]
        return add(household, period, added_components)
