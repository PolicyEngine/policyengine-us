from policyengine_us.model_api import *


class is_medicaid_long_term_care_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid long-term care services"
    definition_period = YEAR
    documentation = (
        "Whether this person is eligible for Medicaid long-term care services "
        "after applying the long-term-care-specific home equity limit. This "
        "does not determine ordinary Medicaid eligibility."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#f",
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
    )

    def formula(person, period, parameters):
        return (
            person("is_medicaid_eligible", period)
            & person("receives_medicaid_long_term_care_services", period)
            & person("is_medicaid_long_term_care_home_equity_eligible", period)
        )
