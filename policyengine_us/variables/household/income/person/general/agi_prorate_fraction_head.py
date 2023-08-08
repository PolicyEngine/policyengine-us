from policyengine_us.model_api import *


class agi_prorate_fraction_head(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income prorate fraction head"
    unit = USD
    definition_period = YEAR

    # get proportion of head's share in the combined federal adjusted gross income.
    def formula(person, period, parameters):
        federal_agi_person = person("adjusted_gross_income_person", period)
        head = person("is_tax_unit_head", period)
        federal_agi_head = head * federal_agi_person
        federal_agi = person.tax_unit("adjusted_gross_income", period)
        # avoid divide-by-zero warnings when using where() function
        prorate_fraction_head = np.zeros_like(federal_agi)
        mask = federal_agi != 0
        prorate_fraction_head[mask] = (
            federal_agi_head[mask] / federal_agi[mask]
        )
        # if no net income, then assign entirely to head.
        return where(
            federal_agi == 0,
            person("is_tax_unit_head", period)[0],
            prorate_fraction_head[0],
        )
