from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    household_has_parent_ids,
    reports_unlinked_children,
)


class medicaid_tax_dependent_exception_living_with_both_parents(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid MAGI tax-dependent exception for a child living with both parents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_ii"

    def formula(person, period, parameters):
        claimed_child = (
            person("is_tax_unit_dependent", period)
            & person("medicaid_non_filer_child_age_eligible", period)
            & person("medicaid_claimed_by_parent_in_tax_unit", period)
        )
        legacy_proxy = (person.family.sum(person("is_parent", period)) > 1) & (
            person.tax_unit.sum(person("is_parent", period)) == 1
        )
        own_ids = has_parent_ids(person, period)
        if not np.any(own_ids):
            return claimed_child & legacy_proxy

        # Living with both parents requires both to resolve in the household.
        first, second = co_resident_parent_indices(person, period)
        two_parents = (first >= 0) & (second >= 0)
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
        # In a household with parent links, the family proxy for a child
        # without ids counts only parents with children the links omit.
        unlinked_parent = reports_unlinked_children(person, period)
        residual_proxy = (person.family.sum(unlinked_parent) > 1) & (
            person.tax_unit.sum(unlinked_parent) == 1
        )
        return claimed_child & where(
            own_ids,
            two_parents & ~parents_file_jointly,
            where(
                household_has_parent_ids(person, period),
                residual_proxy,
                legacy_proxy,
            ),
        )
