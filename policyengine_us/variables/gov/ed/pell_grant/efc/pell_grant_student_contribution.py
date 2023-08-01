
from policyengine_us.model_api import *


class pell_grant_student_contribution(Variable):
    value_type = float
    entity = Person
    label = "Student Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        assets = person("pell_grant_student_assets", period)
        income = person("pell_grant_student_available_income", period)
        allowances = person("pell_grant_student_allowances", period)
        ajusted_income = (income - allowances) * .5
        ajusted_assets = assets * .2
        return ajusted_income + ajusted_assets
