from policyengine_us.model_api import *


def create_ctc_older_child_supplement() -> Reform:
    class ctc_child_individual_maximum(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child)"
        unit = USD
        documentation = (
            "The CTC entitlement in respect of this person as a child."
        )
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/24#a",
            "https://www.law.cornell.edu/uscode/text/26/24#h",
            "https://www.law.cornell.edu/uscode/text/26/24#i",
        )

        def formula(person, period, parameters):
            age = person("age", period)
            base_amount = parameters(period).gov.irs.credits.ctc.amount.base
            is_dependent = person("is_tax_unit_dependent", period)
            base_amount = base_amount.calc(age)
            child_index = person("child_index", period)
            p_ref = parameters(period).gov.contrib.ctc.oldest_child_supplement
            supplement = where(child_index == 1, p_ref.amount, 0)
            return (base_amount + supplement) * is_dependent

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_child_individual_maximum)

    return reform


def create_ctc_older_child_supplement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_older_child_supplement()

    p = parameters(period).gov.contrib.ctc.oldest_child_supplement

    if p.in_effect:
        return create_ctc_older_child_supplement()
    else:
        return None


ctc_older_child_supplement = create_ctc_older_child_supplement_reform(
    None, None, bypass=True
)
