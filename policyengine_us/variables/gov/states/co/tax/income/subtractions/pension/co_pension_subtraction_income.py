from policyengine_us.model_api import *


class co_pension_subtraction_income(Variable):
    value_type = float
    entity = Person
    label = "Income for the Colorado pension and annuity subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = "gov.states.co.tax.income.subtractions.pension.income_sources"
