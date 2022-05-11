from openfisca_us.model_api import *


class medicaid(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Estimated benefit amount from Medicaid (average amount per person from State expenditure)."
    label = "Medicaid benefit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"

    def formula(person, period, parameters):
        eligible = person("is_medicaid_eligible", period)
        state_code = person.household("state_code_str", period)
        medicaid = parameters(period).hhs.medicaid
        average_payment_per_person = (
            medicaid.benefit.total_spending[state_code]
            / medicaid.benefit.total_population[state_code]
        )
        return eligible * average_payment_per_person
