from policyengine_us.model_api import *


class ca_marin_general_relief_liquid_asset_limit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    label = "Limit for the Marin County General Relief liquid asset requirements"
    defined_for = "in_marin"
    reference = (
        "https://www.marincounty.gov/news-releases/county-general-relief-transitions-board-approved-standards-aid-regulations",
        "https://hhs.marincounty.gov/services/get-cash-assistance-myself-general-relief/general-relief-cash-assistance",
    )

    def formula(spm_unit, period, parameters):
        # Month-defined so the July 1, 2025 increase ($200/$400 -> $400/$800) is
        # applied from that month, instead of being masked by the January value
        # a year-defined parameter lookup would read for all of 2025.
        married = spm_unit("spm_unit_is_married", period.this_year)
        p = parameters(
            period
        ).gov.local.ca.marin.general_relief.eligibility.limit.liquid_assets
        return where(married, p.married, p.single)
