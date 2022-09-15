from openfisca_us.model_api import *


class ma_covid_19_essential_employee_premium_pay_program(Variable):
    value_type = float
    entity = Person
    label = "MA COVID 19 Essential Employee Premium Pay Program"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/covid-19-essential-employee-premium-pay-program"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        earnings = person("earned_income", period)
        tax_unit = person.tax_unit
        agi = tax_unit("adjusted_gross_income", period)
        fpg = tax_unit("tax_unit_fpg", period)
        poverty_ratio = agi / fpg
        p = parameters(
            period
        ).gov.states.ma.tax.income.credits.covid_19_essential_employee_premium_pay_program
        meets_earnings_test = earnings >= p.min_earnings
        meets_poverty_ratio_test = poverty_ratio <= p.max_poverty_ratio
        meets_program_test = add(person, period, p.disqualifying_programs) == 0
        in_ma = person.household("state_code_str", period) == "MA"
        eligible = (
            meets_earnings_test
            & meets_poverty_ratio_test
            & meets_program_test
            & in_ma
        )
        return eligible * p.amount
