from openfisca_us.model_api import *


class ctc_child_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (child)"
    unit = "currency-USD"
    documentation = "The CTC entitlement in respect of this person as a child."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        age = person("age", period)
        is_child = age <= ctc.child.max_age
        return is_child * ctc.child.amount

    def formula_2021(person, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        age = person("age", period)
        is_child = age <= ctc.child.max_age
        is_young_child = age <= ctc.child.young.max_age
        return (
            is_young_child * ctc.child.young.increase
            + is_child * ctc.child.amount
        )

    formula_2022 = formula
