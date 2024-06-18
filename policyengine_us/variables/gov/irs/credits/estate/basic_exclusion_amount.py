from policyengine_us.model_api import *


class basic_exclusion_amount(Variable):
    value_type = float
    entity = Person
    label = "Basic exclusion amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.estate
        real_estate_tax = person("real_estate_taxes", period)

        deceased_year = person("year_of_deceased", period)
        deceased_year_eligible = (deceased_year >= p.increase.start_year) & (
            deceased_year <= p.increase.end_year
        )

        basic_amount = where(
            deceased_year_eligible, p.increase.amount, p.basic
        )
        return min_(real_estate_tax, basic_amount)
