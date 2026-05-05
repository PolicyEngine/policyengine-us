from policyengine_us.model_api import *


class medicaid_tax_dependent_exception_living_with_both_parents(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid MAGI tax-dependent exception for a child living with both parents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_ii"

    def formula(person, period, parameters):
        return (
            person("is_tax_unit_dependent", period)
            & person("medicaid_non_filer_child_age_eligible", period)
            & person("medicaid_claimed_by_parent_in_tax_unit", period)
            & (person.family.sum(person("is_parent", period)) > 1)
            & (person.tax_unit.sum(person("is_parent", period)) == 1)
        )
