from policyengine_us.model_api import *


class pell_grant_dependents_in_college(Variable):
    value_type = int
    entity = TaxUnit
    label = "Pell Grant dependents in college"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        people = tax_unit.members
        college_student = people("is_full_time_college_student", period)
        is_head = people("is_tax_unit_head", period)
        is_spouse = people("is_tax_unit_spouse", period)
        is_parent = is_head | is_spouse
        return tax_unit.sum(~is_parent * college_student)
