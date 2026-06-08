from policyengine_us.model_api import *


class hi_ccap_maximum_monthly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Hawaii CCAP maximum monthly payment rate per child"
    definition_period = MONTH
    defined_for = "hi_ccap_eligible_child"
    reference = "https://humanservices.hawaii.gov/wp-content/uploads/2018/04/Child-Care-Rate-Table-2017-08-01.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.rates
        provider_category = person("hi_ccap_provider_category", period)
        hours_tier = person("hi_ccap_hours_tier", period)
        return p.rates[provider_category][hours_tier]
