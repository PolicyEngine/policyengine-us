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
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145"
    defined_for = StateCode.WI

    def formula(person, period, parameters):
        # A pregnant adult meets the TANF test in their own right, which doesn't
        # make their parent a custodial parent.
        dependent_child = person("is_person_demographic_tanf_eligible", period) & (
            ~person("is_pregnant", period) | person("is_child", period.this_year)
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
