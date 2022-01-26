from openfisca_us.model_api import *


class ctc_refundable_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "Maximum refundable CTC"
    unit = "currency-USD"
    documentation = "The maximum refundable CTC for this person."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        return person("ctc_individual_maximum", period)

    def formula_2018(person, period, parameters):
        amount = person("ctc_individual_maximum", period)
        ctc = parameters(period).irs.credits.child_tax_credit
        return min_(amount, ctc.refundable.individual_max)
    
    def formula_2021(person, period, parameters):
        return person("ctc_child_individual_maximum", period)
    
    formula_2022 = formula_2018

    formula_2026 = formula

class refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable CTC"
    unit = "currency-USD"
    documentation = "The portion of the Child Tax Credit that is refundable."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

    def formula(tax_unit, period, parameters):
        pass