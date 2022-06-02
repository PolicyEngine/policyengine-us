from openfisca_us.model_api import *


class ctc_child_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (child)"
    unit = USD
    documentation = "The CTC entitlement in respect of this person as a child."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        return person("is_ctc_qualifying_child", period) * ctc.child.amount

    def formula_2021(person, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        age = person("age", period)
        is_child = person("is_ctc_qualifying_child", period)
        is_young_child = age <= ctc.child.young.max_age
        return (
            is_young_child * ctc.child.young.increase
            + is_child * ctc.child.amount
        )

    formula_2022 = formula
