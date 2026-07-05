from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ar_dependent_credit() -> Reform:
    class ar_personal_credit_dependent(Variable):
        value_type = float
        entity = Person
        label = "Arkansas personal tax credit dependent amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AR

        def formula(person, period, parameters):
            # Separate the dependent portion of the personal tax credit so its
            # per-dependent amount can be set independently. An optional age
            # limit zeroes the credit for dependents at or over the threshold
            # age; this person-level amount is summed via adds in
            # ar_personal_credits_potential, so the age gate composes.
            p = parameters(period).gov.contrib.states.ar.dependent_credit
            is_dependent = person("is_tax_unit_dependent", period)
            if p.age_limit.in_effect:
                age = person("age", period)
                eligible = is_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_dependent
            return eligible * p.amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ar_personal_credit_dependent)

    return reform


def create_ar_dependent_credit_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ar_dependent_credit()

    p = parameters.gov.contrib.states.ar.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ar_dependent_credit()
    else:
        return None


ar_dependent_credit_reform = create_ar_dependent_credit_reform_fn(
    None, None, bypass=True
)
