from policyengine_us.model_api import *


def exclude_from_total(system, total: str, component: str) -> None:
    """Redefine the ``adds`` variable ``total`` without ``component``.

    The remaining components are read from the definition of ``total`` that
    ``system`` holds when the reform is applied, not from a second list. A
    component added to the baseline total therefore reaches the reformed
    total too, and two reforms that each exclude a component of the same
    total combine, where a fixed list would let the later one overwrite the
    earlier one.

    Excluding a component that is already absent changes nothing.
    ``CountryTaxBenefitSystem`` applies a reform more than once, so this must
    hold.
    """
    current = system.get_variable(total, check_existence=True)
    # The replacement inherits any formula of `current`, and a formula is
    # computed in place of `adds`, so editing the list would then do nothing.
    if current.formulas or not isinstance(current.adds, list):
        raise ValueError(
            f"{total} must be an `adds` list with no formula for a reform to "
            f"exclude {component} from it."
        )
    # A new list: `current.adds` belongs to the variable being replaced.
    remaining = [name for name in current.adds if name != component]
    # `update_variable` inherits every attribute the new class leaves out.
    system.update_variable(type(total, (Variable,), {"adds": remaining}))
