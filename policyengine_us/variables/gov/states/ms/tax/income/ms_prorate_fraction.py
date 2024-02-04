from policyengine_us.model_api import *


class ms_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Share of Mississippi AGI within tax unit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        agi = person("ms_agi", period)
        total_agi = person.tax_unit.sum(agi)
        # avoid divide-by-zero warnings when using where() function
        fraction = np.zeros_like(total_agi)
        mask = total_agi != 0
        fraction[mask] = agi[mask] / total_agi[mask]
        # if no net income, then assign entirely to head.
        return where(
            total_agi == 0,
            person("is_tax_unit_head", period),
            fraction,
        )
