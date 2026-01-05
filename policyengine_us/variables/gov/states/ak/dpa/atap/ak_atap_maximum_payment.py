from policyengine_us.model_api import *


class ak_atap_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP maximum payment"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap.payment
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        num_dependents = spm_unit.sum(dependent)
        additional_children = max_(num_dependents - 1, 0)

        # $821 base + $102 per additional child
        # Must have at least 1 dependent to be eligible
        payment = p.base + additional_children * p.additional_child
        return where(num_dependents >= 1, payment, 0)
