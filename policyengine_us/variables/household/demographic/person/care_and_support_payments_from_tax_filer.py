from policyengine_us.model_api import *


class care_and_support_payments_from_tax_filer(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Amount of payments made by the tax filer for this person's care and support"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
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
