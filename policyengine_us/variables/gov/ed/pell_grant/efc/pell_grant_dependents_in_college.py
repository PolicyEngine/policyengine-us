from policyengine_us.model_api import *


class pell_grant_dependents_in_college(Variable):
    value_type = int
    entity = TaxUnit
    label = "Pell Grant dependents in college"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        college_student = person("is_full_time_college_student", period)
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(is_dependent * college_student)
