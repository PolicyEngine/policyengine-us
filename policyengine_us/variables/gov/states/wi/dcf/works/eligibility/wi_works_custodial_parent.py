from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    household_has_parent_ids,
)


class wi_works_custodial_parent(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin Works custodial parent"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/141",
    )
    defined_for = StateCode.WI

    def formula(person, period, parameters):
        # Wis. Stat. 49.141(1)(c): under 18, or under 19 in secondary school. This
        # is the TANF age test without its pregnancy clause, because a pregnant
        # adult doesn't make their own parent a custodial parent.
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        in_school = person("is_in_secondary_school", period)
        dependent_child = person("age", period.this_year) < where(
            in_school, p.student, p.non_student
        )
        unit = person.spm_unit.reference_entity.members_entity_id
        custodial = np.zeros(person.count, dtype=bool)
        for parent in co_resident_parent_indices(person, period.this_year):
            rows = dependent_child & (parent >= 0) & (unit[parent] == unit)
            custodial = custodial | (
                np.bincount(parent[rows], minlength=person.count) > 0
            )
        # Without parent links every parent in the unit counts as custodial.
        return where(
            household_has_parent_ids(person, period.this_year),
            custodial,
            person("is_parent", period.this_year),
        )
