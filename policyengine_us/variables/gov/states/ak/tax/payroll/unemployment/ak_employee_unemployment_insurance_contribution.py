from policyengine_us.model_api import *


class ak_employee_unemployment_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "Alaska employee unemployment insurance contribution"
    documentation = (
        "Alaska employee contribution to the unemployment compensation fund, "
        "withheld from the same wages, up to the taxable wage base, on which "
        "the employer contributes. The rate is 27% of the average benefit cost "
        "rate, between 0.5% and 1%."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/basis/statutes.asp?media=print&secStart=23.20.290&secEnd=23.20.290",
        "https://www.akleg.gov/basis/statutes.asp?media=print&secStart=23.20.175&secEnd=23.20.175",
    )

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.ak.tax.payroll.unemployment.employee_rate
        return rate * person("taxable_earnings_for_state_unemployment_tax", period)
