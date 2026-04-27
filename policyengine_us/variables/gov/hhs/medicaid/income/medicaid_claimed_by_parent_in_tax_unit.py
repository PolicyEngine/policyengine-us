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
        # PolicyEngine US only has a direct parent signal here when household
        # relationship inputs such as own_children_in_household are populated.
        return person("is_tax_unit_dependent", period) & (
            person.tax_unit.sum(person("is_parent", period)) > 0
        )
