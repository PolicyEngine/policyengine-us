from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_total_modifications(Variable):
    value_type = float
    entity = Person
    label = "West Virginia total modifications for the senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = "gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction.modification_sources"
