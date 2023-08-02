from policyengine_us.model_api import *


class pell_grant_student_allowances(Variable):
    value_type = float
    entity = Person
    label = "Student Allowances"
    definition_period = YEAR

    def formula(person, period, parameters):
        other_allowances = person("pell_grant_student_other_allowances", period)
        ipa = parameters(period).gov.ed.pell_grant.efc.student.ipa
        parent_available_income = person("pell_grant_parent_available_income", period)
        allowances_from_parent = where(parent_available_income < 0, -parent_available_income, 0)
        return ipa + allowances_from_parent + other_allowances
