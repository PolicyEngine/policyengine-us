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
        average_payment_per_person = person("medicaid_average_payment", period)
        return eligible * average_payment_per_person
