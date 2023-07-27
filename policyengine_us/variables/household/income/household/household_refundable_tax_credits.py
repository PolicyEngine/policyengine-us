from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD
    adds = [
        "income_tax_refundable_credits",  # Federal.
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
        "nm_refundable_credits",  # New Mexico.
        "ny_refundable_credits",  # New York.
        "or_refundable_credits",  # Oregon.
        # Skip PA, which has no refundable credits.
        "wa_refundable_credits",  # Washington.
        "nyc_refundable_credits",  # New York City.
        "ut_refundable_credits",  # Utah.
        "wi_refundable_credits",  # Wisconsin.
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
