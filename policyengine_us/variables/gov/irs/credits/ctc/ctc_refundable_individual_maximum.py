from policyengine_us.model_api import *


class ctc_refundable_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "Maximum refundable CTC"
    unit = USD
    documentation = "The maximum refundable CTC for this person."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(person, period, parameters):
        amount = person("ctc_child_individual_maximum", period)
        ctc = parameters(period).gov.irs.credits.ctc
        return min_(amount, ctc.refundable.individual_max)
