from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_relationships


class wi_cts_caretaker_children(Variable):
    value_type = int
    entity = Person
    label = "Wisconsin CTS eligible children in this SSI parent's assistance group"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/document/statutes/49.775",
        # PDF pages 20, 68-71
        "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=20",
    )
    documentation = "Each eligible child counts for one co-resident SSI parent. A child in common counts for the parent with more eligible children, and ties go to the lower person_id. Without parent links one SSI parent per family receives the award."

    def formula(person, period, parameters):
        first, second, linked, receipt, _, _ = cts_relationships(person, period)
        child = person("wi_cts_child_eligible", period) & person(
            "wi_cts_sfu_member", period
        )
        count = person.count
        own_children = np.zeros(count)
        for parent in (first, second):
            rows = child & (parent >= 0)
            own_children = own_children + np.bincount(parent[rows], minlength=count)
        # Wis. Stat. 49.775(3) pays once for a child in common, and Handbook
        # 3.1.8 codes one parent as caring for it. Scenarios 3 to 6 give it to
        # the parent with the most children.
        person_id = person("person_id", period.this_year)
        first_cares = (own_children[first] > own_children[second]) | (
            (own_children[first] == own_children[second])
            & (person_id[first] < person_id[second])
        )
        caretaker = where((second < 0) | ((first >= 0) & first_cares), first, second)
        rows = child & (caretaker >= 0)
        linked_children = np.bincount(caretaker[rows], minlength=count)
        candidate = person("is_parent", period.this_year) & receipt
        index = np.arange(count)
        payee = candidate & (index == person.family.min(where(candidate, index, count)))
        return where(linked, linked_children, payee * person.family.sum(child))
