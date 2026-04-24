from policyengine_us.model_api import *


class wa_pfml_average_weekly_wage(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML average weekly wage"
    documentation = (
        "Employee's average weekly wage for Washington Paid Family and "
        "Medical Leave. Simplified as annual employment income divided by "
        "the number of weeks in a year and rounded down to the next lower "
        "dollar."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
    )

    def formula(person, period, parameters):
        override = person("wa_pfml_average_weekly_wage_override", period)
        proxy_aww = np.floor(person("employment_income", period) / WEEKS_IN_YEAR)
        return where(override >= 0, np.floor(override), proxy_aww)
