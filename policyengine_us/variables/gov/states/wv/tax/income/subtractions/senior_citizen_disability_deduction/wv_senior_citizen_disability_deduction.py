from policyengine_us.model_api import *


class wv_total_modification(Variable):
    value_type = float
    entity = Person
    label = "West Virginia total modification as a limit for senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = "gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction.wv_senior_citizen_disability_deduction_person"
