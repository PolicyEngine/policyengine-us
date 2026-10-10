def exclude_from_total(system, total: str, component: str) -> None:
    """Redefine the ``adds`` variable ``total`` without ``component``.

    The replacement is a clone of the definition of ``total`` that ``system``
    holds when the reform is applied, with ``component`` taken out of its
    ``adds`` list. There is no second list: a component added to the baseline
    total reaches the reformed total too, and two reforms that each exclude a
    component of the same total combine, where a fixed list would let the
    later one overwrite the earlier one.

    Excluding a component that is already absent leaves the definition as it
    was. ``CountryTaxBenefitSystem`` applies a reform more than once, so this
    must hold.
    """
    current = system.get_variable(total, check_existence=True)
    # A formula is computed in place of `adds`, so editing the list of a
    # total that has one would do nothing.
    if current.formulas or not isinstance(current.adds, list):
        raise ValueError(
            f"{total} must be an `adds` list with no formula for a reform to "
            f"exclude {component} from it."
        )
    # A clone, as in `TaxBenefitSystem.neutralize_variable`, keeps every other
    # attribute. A new class passed to `update_variable` would not: it drops
    # `defined_for`, for one.
    replacement = current.clone()
    # A new list: `current.adds` belongs to the variable being replaced.
    replacement.adds = [name for name in current.adds if name != component]
    system.variables[total] = replacement
    system.data_modified = True
