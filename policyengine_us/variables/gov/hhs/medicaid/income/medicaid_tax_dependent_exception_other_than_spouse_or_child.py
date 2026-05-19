from policyengine_us.model_api import *


class medicaid_tax_dependent_exception_other_than_spouse_or_child(Variable):
    value_type = bool
    entity = Person
    label = (
        "Medicaid MAGI tax-dependent exception for someone other than a spouse or child"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_i"

    def formula(person, period, parameters):
        return person("is_tax_unit_dependent", period) & ~person(
            "medicaid_claimed_by_parent_in_tax_unit", period
        )
