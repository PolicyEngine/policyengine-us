from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class va_medicaid_lifc_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Virginia Medicaid LIFC income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.dmas.virginia.gov/media/0aynyhxk/m04-1-1-26a.pdf#page=51"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dmas.medicaid.lifc.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)

        group1_limit = (
            p.group1.main[capped_size] + additional_people * p.group1.additional
        )
        group2_limit = (
            p.group2.main[capped_size] + additional_people * p.group2.additional
        )
        group3_limit = (
            p.group3.main[capped_size] + additional_people * p.group3.additional
        )

        locality_group = person.household("va_medicaid_lifc_locality_group", period)
        groups = locality_group.possible_values
        income_limit = select(
            [
                locality_group == groups.GROUP_I,
                locality_group == groups.GROUP_II,
                locality_group == groups.GROUP_III,
            ],
            [group1_limit, group2_limit, group3_limit],
            default=group1_limit,
        )
        state_group = person.household("state_group_str", period)
        return income_limit / fpg(size, state_group, period, parameters)
