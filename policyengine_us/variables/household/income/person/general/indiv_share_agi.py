from policyengine_us.model_api import *


class indiv_share_agi(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income prorate fraction"
    unit = USD
    definition_period = YEAR

    # get proportion of head's share in the combined federal adjusted gross income.
    def formula(person, period, parameters):
        # person = tax_unit.members
        federal_agi_person = person("adjusted_gross_income_person", period)
        federal_agi = np.full_like(
            federal_agi_person,
            person.tax_unit("adjusted_gross_income", period),
        )
        # avoid divide-by-zero warnings when using where() function
        prorate_fraction_head = np.zeros_like(federal_agi_person)
        mask = federal_agi != 0
        prorate_fraction_head[mask] = (
            federal_agi_person[mask] / federal_agi[mask]
        )
        # if no federal agi, then assign entirely to head.
        return where(
            federal_agi == 0,
            person("is_tax_unit_head", period),
            prorate_fraction_head,
        )
