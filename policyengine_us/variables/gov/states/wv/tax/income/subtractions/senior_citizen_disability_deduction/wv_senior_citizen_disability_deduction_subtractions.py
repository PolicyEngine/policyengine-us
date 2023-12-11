from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_subtractions(Variable):
    value_type = float
    entity = Person
    label = "West Virginia senior citizen or disability deduction subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = "gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction.subtractions"
