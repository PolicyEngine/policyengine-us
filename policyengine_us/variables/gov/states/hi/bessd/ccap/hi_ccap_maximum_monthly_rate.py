from policyengine_us.model_api import *


class hi_ccap_maximum_monthly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Hawaii CCAP maximum monthly payment rate per child"
    definition_period = MONTH
    defined_for = "hi_ccap_eligible_child"
    reference = "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=71"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.rates
        provider_category = person("hi_ccap_provider_category", period)
        hours_tier = person("hi_ccap_hours_tier", period)
        rate = p.rates[provider_category][hours_tier]
        # Exhibit I's casual band starts at 1 monthly hour, so a child with no
        # authorized care hours (no care need) receives no payment.
        monthly_care_hours = person("hi_ccap_monthly_care_hours", period)
        return where(monthly_care_hours >= 1, rate, 0)
