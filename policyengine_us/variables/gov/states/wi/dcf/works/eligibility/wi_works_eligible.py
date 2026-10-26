from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    household_has_parent_ids,
)


class wi_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Works eligible"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.02.1_List_of_Criteria.htm",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        demographic = spm_unit("is_demographic_tanf_eligible", period)
        person = spm_unit.members
        is_qualified = person("is_citizen_or_legal_immigrant", period.this_year)
        citizenship = spm_unit.any(is_qualified)
        income = spm_unit("wi_works_income_eligible", period)
        resources = spm_unit("wi_works_resources_eligible", period)
        # Wis. Stat. 49.145(2)(a) and (i): the applicant is a custodial parent
        # who does not receive SSI. Grandfathered state-only SSI recipients
        # are not modeled.
        ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        dependent_child = person("is_person_demographic_tanf_eligible", period)
        unit = spm_unit.members_entity_id
        custodial = np.zeros(person.count, dtype=bool)
        for parent in co_resident_parent_indices(person, period.this_year):
            rows = dependent_child & (parent >= 0) & (unit[parent] == unit)
            custodial = custodial | (
                np.bincount(parent[rows], minlength=person.count) > 0
            )
        # Without parent links every parent in the unit counts as custodial.
        custodial = where(
            household_has_parent_ids(person, period.this_year),
            custodial,
            person("is_parent", period.this_year),
        )
        # SSI receipt excludes the applicant, not an otherwise eligible
        # co-parent or a household merely containing a child on SSI.
        all_custodial_parents_on_ssi = spm_unit.any(
            custodial & ssi_recipient
        ) & ~spm_unit.any(custodial & ~ssi_recipient)
        return (
            demographic
            & citizenship
            & income
            & resources
            & ~all_custodial_parents_on_ssi
        )
