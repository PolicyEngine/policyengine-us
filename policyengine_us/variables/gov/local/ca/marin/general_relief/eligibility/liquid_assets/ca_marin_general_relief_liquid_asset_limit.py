from policyengine_us.model_api import *


class ca_marin_general_relief_liquid_asset_limit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
    label = "Limit for the Marin County General Relief liquid asset requirements"
    defined_for = "in_marin"
    reference = (
        "https://www.marincounty.gov/news-releases/county-general-relief-transitions-board-approved-standards-aid-regulations",
        "https://hhs.marincounty.gov/services/get-cash-assistance-myself-general-relief/general-relief-cash-assistance",
    )

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"]) > 0
        p = parameters(
            period
        ).gov.local.ca.marin.general_relief.eligibility.limit.liquid_assets
        return where(married, p.married, p.single)
