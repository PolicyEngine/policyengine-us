from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._medicaid_parents import (
    medicaid_parent_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    has_parent_ids,
    unlinked_parent,
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
        # For a child without ids, the family and tax unit proxies count only
        # parents some of whose children no parent id names; without links
        # this is is_parent.
        parent = unlinked_parent(person, period)
        proxy = (person.family.sum(parent) > 1) & (person.tax_unit.sum(parent) == 1)
        own_ids = has_parent_ids(person, period)
        if not np.any(own_ids):
            return claimed_child & proxy

        # Living with both parents requires both to resolve in the household.
        # 42 CFR 435.603(b) counts step parents, so a lone named parent's
        # established co-resident spouse is the other parent.
        first, second = medicaid_parent_indices(person, period)
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
        # A known claiming tax unit elsewhere claims the child by a parent when
        # a co-resident parent is its head or spouse.
        tax_unit_id = person.tax_unit("tax_unit_id", period)
        claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
        head_or_spouse = head | spouse
        claimed_elsewhere = person("medicaid_has_known_claiming_tax_unit", period) & (
            claiming_tax_unit_id != tax_unit_id
        )
        claimed_elsewhere_by_parent = claimed_elsewhere & (
            (
                (first >= 0)
                & head_or_spouse[first]
                & (tax_unit_id[first] == claiming_tax_unit_id)
            )
            | (
                (second >= 0)
                & head_or_spouse[second]
                & (tax_unit_id[second] == claiming_tax_unit_id)
            )
        )
        linked = (
            (
                claimed_child
                | (
                    person("medicaid_non_filer_child_age_eligible", period)
                    & claimed_elsewhere_by_parent
                )
            )
            & two_parents
            & ~parents_file_jointly
        )
        return where(own_ids, linked, claimed_child & proxy)
