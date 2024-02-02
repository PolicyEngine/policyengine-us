from policyengine_us.model_api import *


class ms_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Mississippi joint amount proration fraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        net_income = person("ms_agi", period)
        total_net_income = person.tax_unit.sum(net_income)
        # avoid divide-by-zero warnings when using where() function
        fraction = np.zeros_like(total_net_income)
        mask = total_net_income != 0
        fraction[mask] = net_income[mask] / total_net_income[mask]
        # if no net income, then assign entirely to head.
        return where(
            total_net_income == 0,
            person("is_tax_unit_head", period),
            fraction,
        )
