from policyengine_us.model_api import *


class ca_marin_general_relief_liquid_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Marin County General Relief based on the liquid asset requirements"
    defined_for = "in_marin"
    reference = "https://www.marincounty.gov/news-releases/county-general-relief-transitions-board-approved-standards-aid-regulations"

    def formula(spm_unit, period, parameters):
        # Month-defined so the limit picks up the mid-year increase. Cash assets
        # are a year-defined stock, so read them with period.this_year to avoid
        # dividing the balance across months.
        cash = spm_unit("spm_unit_cash_assets", period.this_year)
        limit = spm_unit("ca_marin_general_relief_liquid_asset_limit", period)
        return cash <= limit
