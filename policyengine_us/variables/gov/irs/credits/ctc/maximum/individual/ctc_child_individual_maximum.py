from policyengine_us.model_api import *


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
        ctc = parameters(period).gov.irs.credits.ctc
        is_child = person("is_ctc_qualifying_child", period)
        base_amount = is_child * ctc.child.amount
        is_young_child = person("is_ctc_qualifying_young_child", period)
        young_child_amount = is_young_child * ctc.child.young.increase
        return base_amount + young_child_amount
