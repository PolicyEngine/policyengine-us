from policyengine_us.model_api import *


class ms_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Share of Mississippi AGI within tax unit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        # We will allocate the itemized deduction by first closing the
        # between the head and spouse income and then allocating 
        # it evenly 
        agi = person("ms_agi", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_agi = agi * head
        spouse_agi = agi * spouse
        agi_difference = np.abs(head_agi - spouse_agi)

        unit_deds = person.tax_unit("ms_itemized_deductions_unit", period)
        deductions_capped_at_agi_difference = min_(
            agi_difference, unit_deds
        )
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

