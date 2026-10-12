from policyengine_us.model_api import *


class ut_ccap_market_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Utah CCAP maximum monthly market rate per child"
    definition_period = MONTH
    defined_for = "ut_ccap_eligible_child"
    reference = (
        "https://jobs.utah.gov/occ/provider/table30824.pdf",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-713",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.rates
        provider_type = person("ut_ccap_provider_type", period)
        age_group = person("ut_ccap_age_group", period)
        return p.market_rate[provider_type][age_group]
