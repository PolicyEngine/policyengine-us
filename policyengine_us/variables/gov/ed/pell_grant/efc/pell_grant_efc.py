from policyengine_us.model_api import *


class pell_grant_efc(Variable):
    value_type = float
    entity = Person
    label = "Expected Family Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        parent_contribution = person("pell_grant_parent_contribution", period)
        student_contribution = person("pell_grant_student_contribution", period)
        parent_income = person("pell_grant_parent_income", period)
        zero_efc_max = parameters(period).gov.ed.pell_grant.efc.automatic_zero
        efc = where(parent_income <= zero_efc_max, 0, parent_contribution + student_contribution)
        return efc

'''
    efc = parent_contrib + student_contrib + student_assets
*   student_contrib = (total_income - total_allowances) * .5
*   student_assets = net_worth * .2
    parrent_contrib = calc_contribution(parrent_available_income + parent_assets) / students_in_college
    parent_available_income = total_income - allowances
    parent_assets = net_worth * .12
'''