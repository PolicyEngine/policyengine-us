from policyengine_us.model_api import *


class medicaid_claimed_by_parent_in_tax_unit(Variable):
    value_type = bool
    entity = Person
    label = (
        "Claimed by a parent in the current tax unit for Medicaid MAGI household rules"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"

    def formula(person, period, parameters):
        # In tax-unit-only inputs, child dependents are usually the filer's
        # children even when own_children_in_household is not provided.
        return person("is_tax_unit_dependent", period) & (
            person("is_qualifying_child_dependent", period)
            | (person.tax_unit.sum(person("is_parent", period)) > 0)
        )
