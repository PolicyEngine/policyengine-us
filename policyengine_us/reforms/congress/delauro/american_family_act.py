from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_american_family_act_with_baby_bonus() -> Reform:
    class ctc_child_individual_maximum_arpa(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child under ARPA)"
        unit = USD
        documentation = "The CTC entitlement in respect of this person as a child, under the American Rescue Plan Act."
        definition_period = YEAR
        defined_for = "ctc_qualifying_child"

        def formula(person, period, parameters):
            age = person("age", period)
            amount_pre_baby_bonus = parameters(
                period
            ).gov.irs.credits.ctc.amount.arpa.calc(age)
            # Add the baby bonus.
            baby_bonus_amount = parameters(
                period
            ).gov.contrib.congress.delauro.american_family_act.baby_bonus
            is_baby = age < 1
            baby_bonus = baby_bonus_amount * is_baby
            return amount_pre_baby_bonus + baby_bonus

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_child_individual_maximum_arpa)

    return reform


def create_american_family_act_with_baby_bonus_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_american_family_act_with_baby_bonus()

    p = parameters.gov.contrib.congress.delauro.american_family_act

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).baby_bonus > 0:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_american_family_act_with_baby_bonus()
    else:
        return None


american_family_act = create_american_family_act_with_baby_bonus_reform(
    None, None, bypass=True
)
