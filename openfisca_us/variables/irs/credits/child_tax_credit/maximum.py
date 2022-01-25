from openfisca_us.model_api import *


class ctc_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC individual amount maximum"
    unit = "currency-USD"
    documentation = (
        "The Child Tax Credit entitlement in respect of this person."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_child = age <= ctc.child.max_age
        return is_child * ctc.child.amount

    def formula_2018(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age <= ctc.child.max_age
        is_adult_dependent = ~is_child & is_dependent
        return (
            is_child * ctc.child.amount
            + is_adult_dependent * ctc.adult_dependent_amount
        )

    def formula_2021(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age <= ctc.child.max_age
        is_young_child = age <= ctc.child.young.max_age
        is_adult_dependent = ~is_child & is_dependent
        return (
            is_young_child * ctc.child.young.increase
            + is_child * ctc.child.amount
            + is_adult_dependent * ctc.adult_dependent_amount
        )

    formula_2022 = formula_2018

    formula_2026 = formula
