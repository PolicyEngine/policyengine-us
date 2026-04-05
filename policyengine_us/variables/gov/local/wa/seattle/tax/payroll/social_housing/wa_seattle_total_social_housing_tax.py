from policyengine_us.model_api import *


class wa_seattle_total_social_housing_tax(Variable):
    value_type = float
    entity = Person
    label = "Total Seattle social housing tax"
    documentation = (
        "Employer-side Seattle Social Housing Tax liability from aggregate "
        "Seattle excess compensation inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.seattle.gov/city-finance/business-taxes-and-licenses/"
        "seattle-taxes/social-housing-tax"
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        excess_compensation = person(
            "employer_total_wa_seattle_social_housing_excess_compensation", period
        )
        rate = parameters(period).gov.local.wa.seattle.tax.payroll.social_housing.rate
        return where(state_code == StateCode.WA, rate * excess_compensation, 0)
