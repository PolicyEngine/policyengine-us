from policyengine_us.model_api import *


class pa_ccw_maximum_monthly_payment(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pennsylvania CCW maximum monthly payment per child"
    definition_period = MONTH
    defined_for = "pa_ccw_eligible_child"
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=32"

    def formula(person, period, parameters):
        daily_rate = person("pa_ccw_market_rate", period)
        days_per_month = person("childcare_attending_days_per_month", period.this_year)
        return daily_rate * days_per_month
