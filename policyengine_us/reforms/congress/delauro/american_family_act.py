from policyengine_us.model_api import *


def create_american_family_act_with_baby_bonus() -> Reform:
    class ctc_child_individual_maximum_arpa(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child under ARPA)"
        unit = USD
        documentation = "The CTC entitlement in respect of this person as a child, under the American Rescue Plan Act."
        definition_period = YEAR

        def formula(person, period, parameters):
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            amount_pre_baby_bonus = parameters(
                period
            ).gov.irs.credits.ctc.amount.arpa.calc(age)
            # Add the baby bonus.
            baby_bonus_amount = parameters(
                period
            ).gov.contrib.congress.delauro.american_family_act.baby_bonus
            is_baby = age == 0
            baby_bonus = baby_bonus_amount * is_baby
            amount = amount_pre_baby_bonus + baby_bonus
            return is_dependent * amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_child_individual_maximum_arpa)

    return reform


def create_american_family_act_with_baby_bonus_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_american_family_act_with_baby_bonus()

    p = parameters(period).gov.contrib.congress.delauro.american_family_act

    if p.baby_bonus > 0:
        return create_american_family_act_with_baby_bonus()
    else:
        return None


american_family_act = create_american_family_act_with_baby_bonus_reform(
    None, None, bypass=True
)
