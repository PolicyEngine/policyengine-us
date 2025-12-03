from policyengine_us.model_api import *


class msp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program eligible"
    definition_period = MONTH
    documentation = (
        "Eligible for any level of the Medicare Savings Program "
        "(QMB, SLMB, or QI)."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        # Must be Medicare eligible
        is_medicare = person("is_medicare_eligible", period.this_year)
        # Must meet income test (at QI level - 135% FPL)
        income_eligible = person("msp_income_eligible", period)
        # Must meet asset test (if applicable in state)
        asset_eligible = person("msp_asset_eligible", period)
        return is_medicare & income_eligible & asset_eligible
