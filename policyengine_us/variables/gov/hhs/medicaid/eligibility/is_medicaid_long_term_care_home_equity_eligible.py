from policyengine_us.model_api import *


class is_medicaid_long_term_care_home_equity_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid long-term care home equity eligible"
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care
        receives_long_term_care = person(
            "receives_medicaid_long_term_care_services", period
        )
        home_is_agricultural = person("home_is_on_agricultural_land", period)
        family_exception = person("medicaid_home_equity_limit_family_exception", period)
        home_equity = person("home_equity", period)
        home_equity_limit = where(
            home_is_agricultural,
            p.home_equity.agricultural_limit,
            p.home_equity.limit,
        )
        return (
            ~receives_long_term_care
            | family_exception
            | (home_equity <= home_equity_limit)
        )
