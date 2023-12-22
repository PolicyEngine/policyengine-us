from policyengine_us.model_api import *


class share_of_care_and_support_costs_paid_by_tax_filer(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "The percentage of care and support costs of a senior paid by the tax filer"

    def formula(person, period, parameters):
        care_and_support_payment = person(
            "care_and_support_payments_from_tax_filer", period
        )
        care_and_support_costs = person("care_and_support_costs", period)
        support_payment_ratio = np.zeros_like(care_and_support_costs)
        mask = care_and_support_costs != 0
        support_payment_ratio[mask] = (
            care_and_support_payment[mask] / care_and_support_costs[mask]
        )
        return support_payment_ratio
