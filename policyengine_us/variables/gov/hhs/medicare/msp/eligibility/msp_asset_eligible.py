from policyengine_us.model_api import *


class msp_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program asset eligible"
    definition_period = MONTH
    documentation = (
        "Eligible for MSP based on asset test. "
        "Some states have eliminated the asset test."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.msp.eligibility.asset
        # Check if asset test applies (some states eliminated it)
        asset_test_applies = p.applies
        # Get assets (yearly variable, use this_year to get full value)
        assets = person.spm_unit("spm_unit_cash_assets", period.this_year)
        # Determine limit based on marital status
        is_married = person.family("is_married", period)
        asset_limit = where(is_married, p.couple, p.individual)
        # Eligible if assets are within limit
        assets_within_limit = assets <= asset_limit
        # If asset test doesn't apply, everyone passes; otherwise check limit
        return where(asset_test_applies, assets_within_limit, True)
