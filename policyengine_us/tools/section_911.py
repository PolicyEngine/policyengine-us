"""Input provenance for Form 2555 amounts."""

from policyengine_core.periods import period as parse_period


SECTION_911_LEAF_INPUTS = (
    "foreign_earned_income_exclusion_amount",
    "foreign_housing_exclusion",
    "foreign_earned_income_exclusion_allocable_deductions",
    "foreign_housing_deduction",
    "foreign_earned_income_exclusion_disallowed_deductions",
)


def validate_section_911_batch_inputs(situation, default_period):
    """Reject ambiguous JSON batches before Core fills omitted inputs with zeros.

    Core stores explicit-input provenance for whole arrays, not individual tax
    units. With both aggregate overrides and leaves, units must have matching
    input-period coverage. Values and the particular leaf components may differ.
    Dataset and setter arrays already describe every entity in the array.
    """
    if situation is None:
        return
    tax_units = situation.get("tax_units", {})
    if len(tax_units) < 2:
        return

    aggregates = (
        "foreign_earned_income_exclusion",
        "section_911_excluded_income",
        "foreign_earned_income_exclusion_gross",
        "ma_foreign_earned_income_exclusion_addback",
    )

    def input_periods(inputs, variable):
        values = inputs.get(variable)
        if values is None:
            return frozenset()
        if not isinstance(values, dict):
            values = {default_period: values}
        return frozenset(
            parse_period(input_period)
            for input_period, value in values.items()
            if value is not None
        )

    signatures = []
    component_periods = {name: set() for name in SECTION_911_LEAF_INPUTS}
    for inputs in tax_units.values():
        aggregate_periods = tuple(input_periods(inputs, name) for name in aggregates)
        leaf_periods = frozenset()
        for name in SECTION_911_LEAF_INPUTS:
            supplied_periods = input_periods(inputs, name)
            leaf_periods |= supplied_periods
            if supplied_periods:
                component_periods[name].add(supplied_periods)
        signatures.append((aggregate_periods, leaf_periods))

    has_aggregates = any(any(aggregate_periods) for aggregate_periods, _ in signatures)
    has_leaves = any(leaf_periods for _, leaf_periods in signatures)
    mixed_representations = (
        has_aggregates
        and has_leaves
        and any(signature != signatures[0] for signature in signatures[1:])
    )
    # A later array for the same leaf also zero-fills another unit's carried
    # amount, even in an otherwise leaf-only batch. Absent components are safe.
    mixed_leaf_periods = any(
        len(coverage) > 1 for coverage in component_periods.values()
    )
    if mixed_representations or mixed_leaf_periods:
        raise ValueError(
            "Batched tax units cannot mix section 911 aggregate or Form 2555 "
            "leaf inputs with different input-period coverage. "
            "Supply consistent aggregate and leaf input periods across tax "
            "units, including explicit zeros, or calculate the units separately."
        )
