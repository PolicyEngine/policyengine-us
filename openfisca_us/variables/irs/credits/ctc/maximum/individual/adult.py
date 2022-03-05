from openfisca_us.model_api import *


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
        ctc = parameters(period).irs.credits.ctc
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        is_child = age <= ctc.child.max_age
        is_adult_dependent = ~is_child & is_dependent
        return is_adult_dependent * ctc.adult_dependent_amount

    formula_2022 = formula_2018

    formula_2026 = None
