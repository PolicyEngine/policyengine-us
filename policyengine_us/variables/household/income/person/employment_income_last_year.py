from policyengine_us.model_api import *


class employment_income_last_year(Variable):
    value_type = float
    entity = Person
    label = "employment income last year"
    documentation = (
        "Wages and salaries in prior year, including tips and commissions."
    )
    unit = USD
    definition_period = YEAR

    def formula_2024(person, period, parameters):
        employment_income_target = (
            parameters.calibration.gov.irs.soi.employment_income
        )
        value_last_year = employment_income_target(period.last_year)
        value_year_before_last = employment_income_target(
            period.last_year.last_year
        )
        values = person("employment_income_last_year", period.last_year)
        uprating_factor = value_last_year / value_year_before_last
        return values * uprating_factor
