from openfisca_us.model_api import *


class claimed_ma_covid_19_essential_employee_premium_pay_program_2020(
    Variable
):
    value_type = bool
    entity = Person
    label = (
        "Claimed MA COVID 19 Essential Employee Premium Pay Program for 2020"
    )
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/covid-19-essential-employee-premium-pay-program"
