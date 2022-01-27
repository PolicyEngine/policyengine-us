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
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_child = age <= ctc.child.max_age
        return is_child * ctc.child.amount

    def formula_2021(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_child = age <= ctc.child.max_age
        is_young_child = age <= ctc.child.young.max_age
        return (
            is_young_child * ctc.child.young.increase
            + is_child * ctc.child.amount
        )

    formula_2022 = formula


class ctc_adult_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (adult dependent)"
    unit = "currency-USD"
    documentation = (
        "The CTC entitlement in respect of this person as an adult dependent."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula_2018(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age <= ctc.child.max_age
        is_adult_dependent = ~is_child & is_dependent
        return is_adult_dependent * ctc.adult_dependent_amount

    formula_2022 = formula_2018

    formula_2026 = None


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
        return person("ctc_child_individual_maximum", period)

    def formula_2018(person, period, parameters):
        return add(
            person,
            period,
            [
                "ctc_child_individual_maximum",
                "ctc_adult_individual_maximum",
            ],
        )

    formula_2026 = formula


class ctc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC"
    unit = "currency-USD"
    documentation = "Maximum value of the Child Tax Credit, before phaseout."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return aggr(tax_unit, period, ["ctc_individual_maximum"])
