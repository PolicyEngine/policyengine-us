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

        # Check for pregnant woman alone (size 1 with pregnant person)
        unit_size = spm_unit("spm_unit_size", period)
        is_pregnant = add(spm_unit, period, ["is_pregnant"]) > 0
        is_pregnant_woman_alone = (unit_size == 1) & is_pregnant

        # Adult-included: $821 base + $102 per additional child
        adult_included_payment = (
            p.base + additional_children * p.additional_child
        )
        adult_included_eligible = num_dependents >= 1

        # Return pregnant woman max payment if alone, otherwise adult-included
        return where(
            is_pregnant_woman_alone,
            p.pregnant_woman,
            where(adult_included_eligible, adult_included_payment, 0),
        )
