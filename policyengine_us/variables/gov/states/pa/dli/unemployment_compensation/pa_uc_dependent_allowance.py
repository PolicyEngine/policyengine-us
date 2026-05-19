from policyengine_us.model_api import *


class pa_uc_dependent_allowance(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation weekly dependent allowance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=159",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # § 404(e)(3): $5 for a dependent spouse OR a first dependent child
        # when there is no dependent spouse; plus $3 for one other dependent
        # child; capped at $8 total per week.
        has_spouse = person("pa_uc_has_dependent_spouse", period)
        num_children = person("pa_uc_dependent_children_count", period)
        p = parameters(
            period
        ).gov.states.pa.dli.unemployment_compensation.dependent_allowance

        # First slot ($5): filled by spouse, or by first child if no spouse.
        first_slot_filled = has_spouse | (num_children >= 1)
        first_amount = where(first_slot_filled, p.spouse_or_first_child, 0)

        # Second slot ($3): filled by one other dependent child.
        # If spouse present: requires at least one child.
        # If no spouse: requires at least two children.
        second_slot_filled = where(
            has_spouse,
            num_children >= 1,
            num_children >= 2,
        )
        second_amount = where(second_slot_filled, p.second_child, 0)

        total = first_amount + second_amount
        return min_(total, p.maximum)
