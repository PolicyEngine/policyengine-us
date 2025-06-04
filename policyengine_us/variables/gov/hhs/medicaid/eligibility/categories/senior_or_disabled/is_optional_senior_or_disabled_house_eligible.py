from policyengine_us.model_api import *


class is_optional_senior_or_disabled_house_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Cash Asset-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        #  Assets
        home_equity = person.household("home_equity", period)  # $

        #  state info
        state = person.household("state_code_str", period)

        #  Parameter path
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        #  Asset limit
        asset_limit = p.assets.limit.home_value[state]

        return home_equity < asset_limit
