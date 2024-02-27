from policyengine_us.model_api import *


class hi_food_excise_credit_child_receiving_public_support(Variable):
    value_type = bool
    entity = Person
    label = "Child received support for the hawaii food excise credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax
        child_support = person("child_support_received", period)
        # Test if the child receive more than half support from public agency
        # (tanf or social_security_survivor_benefits)
        government_payments = add(
            person, period, ["tanf_person", "social_security_survivors"]
        )
        total_income = government_payments + child_support
        # If zero total income, assign 0% public support.
        public_support_percent = np.zeros_like(total_income)
        mask = total_income > 0
        public_support_percent[mask] = (
            government_payments[mask] / total_income[mask]
        )
        return (
            public_support_percent > p.minor_child.support_proportion_threshold
        )
