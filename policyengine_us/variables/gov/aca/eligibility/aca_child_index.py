from policyengine_us.model_api import *


class aca_child_index(Variable):
    value_type = int
    entity = Person
    label = "Index of covered ACA child in tax unit (1 = oldest)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/147.102#c_1"
    documentation = (
        "Rank Marketplace-enrolled children by age, with 1 for the oldest. "
        "Only covered children count toward the three-child premium limit. "
        "Adults and people not enrolled receive the sentinel value 99."
    )

    def formula(person, period, parameters):
        age = person("age", period)
        is_child = age <= parameters(period).gov.aca.slcsp.max_child_age
        covered_child = is_child & person("is_aca_marketplace_enrollee", period)
        child_rank = person.get_rank(person.tax_unit, -age, condition=covered_child)
        # child_rank of 0 ==> oldest; ties broken by order in the tax unit
        NOT_COVERED_CHILD_VALUE = 99
        return where(covered_child, child_rank + 1, NOT_COVERED_CHILD_VALUE)
