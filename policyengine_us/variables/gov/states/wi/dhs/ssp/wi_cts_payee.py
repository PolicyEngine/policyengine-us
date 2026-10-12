from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_relationships


class wi_cts_payee(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS designated SSI parent payee"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "One SSI parent receives the child award. Defaults to the first eligible parent in the family; override the agency-designated payee if different."

    def formula(person, period, parameters):
        first, second, linked, receipt, _, _ = cts_relationships(person, period)
        child = person("wi_cts_child_eligible", period)
        parent_rows = np.concatenate((first[child], second[child]))
        parent_mask = (
            np.bincount(parent_rows[parent_rows >= 0], minlength=person.count) > 0
        )
        candidate = (
            where(linked, parent_mask, person("is_parent", period.this_year)) & receipt
        )
        index = np.arange(person.count)
        first_payee = person.family.min(where(candidate, index, person.count))
        return candidate & (index == first_payee)
