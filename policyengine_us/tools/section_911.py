"""Input provenance and election detection for Form 2555 amounts."""

import numpy as np
from policyengine_core.periods import period as parse_period


SECTION_911_LEAF_INPUTS = (
    "foreign_earned_income_exclusion_amount",
    "foreign_housing_exclusion",
    "foreign_earned_income_exclusion_allocable_deductions",
    "foreign_housing_deduction",
    "foreign_earned_income_exclusion_disallowed_deductions",
)


def has_section_911_leaf_inputs(tax_unit, period):
    """Whether any Form 2555 leaf input applies to the period.

    A leaf supplied for the period or carried from an earlier one counts.
    Core's input export helper tracks supplied values by year and branch, so
    cached default zeros do not count and explicitly supplied zeros do
    (available since core 3.32.8). Every formula that switches between the
    leaves and the legacy aggregates uses this test.
    """
    return any(
        input_period.start <= period.start
        for variable in SECTION_911_LEAF_INPUTS
        for input_period in tax_unit.simulation._get_exportable_input_periods(
            variable, include_computed_variables=False
        )
    )


def section_911_gross_exclusion(tax_unit, period):
    """Amounts excluded from gross income under section 911(a), floored at zero.

    With leaf inputs, this is Form 2555 line 43 (the line 36 housing
    exclusion plus the line 42 foreign earned income exclusion), before the
    line 44 allocable deductions and worksheet line 2b, and without the line
    50 housing deduction, which is a deduction rather than an exclusion.
    Without leaf inputs, the legacy foreign_earned_income_exclusion amount
    (worksheet line 2c) is the fallback. It equals line 43 when lines 44 and
    50 and worksheet line 2b are zero, or when line 50 equals line 44 plus
    line 2b. An exclusion cannot be negative, so neither amount can reduce
    gross income.

    References:
    https://www.law.cornell.edu/uscode/text/26/911#a
    https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3
    https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=37
    """
    if has_section_911_leaf_inputs(tax_unit, period):
        excluded = tax_unit("foreign_earned_income_exclusion_gross", period)
    else:
        excluded = tax_unit("foreign_earned_income_exclusion", period)
    return np.maximum(0, excluded)


def elects_section_911_exclusion(tax_unit, period):
    """Detect a section 911 election from aggregates or Form 2555 leaves.

    Section 911(a)(1) and (2) provide separate earned-income and housing
    exclusion elections, so housing-only filers also elect section 911.
    Positive Form 2555 amounts identify the election even when deductions or
    an explicit aggregate override reduce the federal stacking amount to zero.
    Schedule 8812 (Line 13 and Part II-A) and Publication 596 (Rule 5) bar
    Form 2555 filers from Worksheet B, refundable CTC, and EITC.

    A filer who claims only the section 911(c)(4) housing deduction (Form
    2555 line 50) is also barred. That case rests on the IRS instructions,
    not on the statute. Section 24(d)(3) applies to a taxpayer who "elects
    to exclude any amount from gross income under section 911", and section
    911(c)(4)(A) treats the housing amount as "a deduction allowable in
    computing adjusted gross income", not an exclusion. The Schedule 8812
    instructions bar every Form 2555 filer: Part II-A says "If you file Form
    2555, you cannot claim the additional child tax credit", and Credit
    Limit Worksheet B applies only if "You are not filing Form 2555".
    Publication 596 Rule 5 denies the EITC to anyone who files Form 2555 "to
    deduct or exclude a foreign housing amount"; section 32(c)(1)(C) excludes
    an individual who "claims the benefits of section 911".

    References:
    https://www.law.cornell.edu/uscode/text/26/911#a
    https://www.law.cornell.edu/uscode/text/26/911#c_4
    https://www.law.cornell.edu/uscode/text/26/24#d_3
    https://www.law.cornell.edu/uscode/text/26/32#c_1_C
    https://www.irs.gov/instructions/i1040s8
    https://www.irs.gov/publications/p596
    """
    return np.logical_or.reduce(
        [
            tax_unit(variable, period) > 0
            for variable in (
                "foreign_earned_income_exclusion",
                "section_911_excluded_income",
                *SECTION_911_LEAF_INPUTS,
            )
        ]
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
