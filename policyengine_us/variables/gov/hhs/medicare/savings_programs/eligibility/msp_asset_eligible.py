from policyengine_us.model_api import *


class msp_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program asset eligible"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.medicareinteractive.org/understanding-medicare/"
        "cost-saving-programs/medicare-savings-programs-qmb-slmb-qi/"
        "medicare-savings-program-income-and-asset-limits",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.savings_programs.eligibility
        state_code = person.household("state_code_str", period)
        # Check if asset test applies (some states have eliminated it)
        asset_test_applies = p.asset.applies[state_code]
        # If asset test doesn't apply, everyone is asset-eligible
        cash_assets = person.spm_unit("spm_unit_cash_assets", period.this_year)
        married = person.spm_unit("spm_unit_is_married", period)
        asset_limit = where(married, p.asset.couple, p.asset.individual)
        meets_asset_test = cash_assets <= asset_limit
        return where(asset_test_applies, meets_asset_test, True)
