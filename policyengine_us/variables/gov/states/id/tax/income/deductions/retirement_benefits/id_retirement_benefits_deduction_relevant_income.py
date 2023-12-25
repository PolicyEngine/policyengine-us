from policyengine_us.model_api import *


class id_retirement_benefits_deduction_relevant_income(Variable):
    value_type = float
    entity = Person
    label = "Idaho retirement benefits deduction income sources"
    unit = USD
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/"
    definition_period = YEAR
    defined_for = "id_retirement_benefits_deduction_eligible_person"

    adds = "gov.states.id.tax.income.deductions.retirement_benefits.income_sources"
