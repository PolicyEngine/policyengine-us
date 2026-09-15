from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


class medicaid_tax_dependent_exception_living_with_both_parents(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid MAGI tax-dependent exception for a child living with both parents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_ii"

    def formula(person, period, parameters):
        first, second = co_resident_parent_indices(person, period)
        two_parents = (first >= 0) & (second >= 0) & (first != second)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        parents_file_jointly = (
            (tax_unit[first] == tax_unit[second])
            & ((head[first] & spouse[second]) | (spouse[first] & head[second]))
            & joint[first]
            & person.tax_unit("tax_unit_is_filer", period)[first]
        )
        has_parent_ids = (person("parent_1_id", period) != 0) | (
            person("parent_2_id", period) != 0
        )
        legacy_proxy = (person.family.sum(person("is_parent", period)) > 1) & (
            person.tax_unit.sum(person("is_parent", period)) == 1
        )
        return (
            person("is_tax_unit_dependent", period)
            & person("medicaid_non_filer_child_age_eligible", period)
            & person("medicaid_claimed_by_parent_in_tax_unit", period)
            & where(has_parent_ids, two_parents & ~parents_file_jointly, legacy_proxy)
        )
