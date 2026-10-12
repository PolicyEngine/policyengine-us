from policyengine_us.model_api import *


class mt_ccap_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Montana Best Beginnings Child Care Scholarship maximum monthly rate"
    definition_period = MONTH
    defined_for = "mt_ccap_eligible_child"
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.205",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/documentsandresources/BBSProviderRatesMonthly.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap
        provider_type = person("mt_ccap_provider_type", period)
        age_category = person("mt_ccap_child_age_category", period)
        care_time = person("mt_ccap_care_time", period)
        return p.rates.provider_rates[provider_type][age_category][care_time]
