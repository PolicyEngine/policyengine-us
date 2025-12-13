from policyengine_us.model_api import *


class msp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program eligible"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/cfr/text/42/435.121",
    )

    def formula(person, period, parameters):
        # Must be Medicare eligible
        medicare_eligible = person("is_medicare_eligible", period.this_year)
        income_eligible = person("msp_income_eligible", period)
        asset_eligible = person("msp_asset_eligible", period)

        return medicare_eligible & income_eligible & asset_eligible
