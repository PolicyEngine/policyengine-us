from policyengine_us.model_api import *


class va_agi_share(Variable):
    value_type = float
    entity = Person
    label = "Virginia share of state adjusted gross income of each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=20"
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        agi = person("va_agi_person", period)
        total_agi = person.tax_unit.sum(agi)
        # avoid divide-by-zero warnings
        fraction = np.zeros_like(total_agi)
        mask = total_agi != 0
        fraction[mask] = agi[mask] / total_agi[mask]
        # if no net income, then assign entirely to head.
        return where(
            total_agi == 0,
            person("is_tax_unit_head", period),
            fraction,
        )
